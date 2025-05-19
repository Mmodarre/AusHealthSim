"""
Actuarial data generator for enhanced simulation.
"""
from datetime import date, datetime, timedelta
import random
from typing import Dict, List, Any, Optional

from health_insurance_au.utils.db_utils import execute_query, execute_non_query, bulk_insert
from health_insurance_au.models.models import ActuarialMetric

class ActuarialDataGenerator:
    """Generator for actuarial metrics."""
    
    def __init__(self):
        """Initialize the actuarial data generator."""
        pass
    
    def generate_metrics(self, simulation_date: date) -> Dict[str, int]:
        """
        Generate actuarial metrics.
        
        Args:
            simulation_date: The simulation date
            
        Returns:
            Dictionary with statistics about generated metrics
        """
        # Only generate metrics on the last day of the month
        if not self._is_last_day_of_month(simulation_date):
            return {'metrics_generated': 0}
        
        # Get aggregated data for metrics
        aggregated_data = self._get_aggregated_data(simulation_date)
        
        # Generate metrics
        metrics = []
        
        # Generate loss ratio metrics
        loss_ratio_metrics = self._generate_loss_ratio_metrics(aggregated_data, simulation_date)
        metrics.extend(loss_ratio_metrics)
        
        # Generate lapse rate metrics
        lapse_rate_metrics = self._generate_lapse_rate_metrics(aggregated_data, simulation_date)
        metrics.extend(lapse_rate_metrics)
        
        # Generate acquisition cost metrics
        acquisition_cost_metrics = self._generate_acquisition_cost_metrics(aggregated_data, simulation_date)
        metrics.extend(acquisition_cost_metrics)
        
        # Insert metrics into the database
        metrics_inserted = 0
        if metrics:
            metric_dicts = [m.to_dict() for m in metrics]
            metrics_inserted = bulk_insert("Insurance.ActuarialMetrics", metric_dicts)
        
        return {
            'metrics_generated': metrics_inserted
        }
    
    def _is_last_day_of_month(self, check_date: date) -> bool:
        """Check if a date is the last day of the month."""
        next_day = check_date + timedelta(days=1)
        return check_date.month != next_day.month
    
    def _get_aggregated_data(self, simulation_date: date) -> List[Dict[str, Any]]:
        """Get aggregated data for metrics from the database."""
        try:
            # Get data for the current month
            start_date = date(simulation_date.year, simulation_date.month, 1)
            
            query = """
            SELECT 
                CASE 
                    WHEN DATEDIFF(YEAR, m.DateOfBirth, GETDATE()) < 18 THEN 'Under 18'
                    WHEN DATEDIFF(YEAR, m.DateOfBirth, GETDATE()) BETWEEN 18 AND 30 THEN '18-30'
                    WHEN DATEDIFF(YEAR, m.DateOfBirth, GETDATE()) BETWEEN 31 AND 50 THEN '31-50'
                    WHEN DATEDIFF(YEAR, m.DateOfBirth, GETDATE()) BETWEEN 51 AND 70 THEN '51-70'
                    ELSE '71+'
                END AS AgeGroup,
                m.Gender,
                m.State AS StateTerritory,
                CASE 
                    WHEN cp.HospitalTier = 'Gold' THEN 'Gold'
                    WHEN cp.HospitalTier = 'Silver' THEN 'Silver'
                    WHEN cp.HospitalTier = 'Bronze' THEN 'Bronze'
                    WHEN cp.HospitalTier = 'Basic' THEN 'Basic'
                    ELSE 'Other'
                END AS ProductCategory,
                SUM(pp.PaymentAmount) AS TotalPremiums,
                SUM(c.InsuranceAmount) AS TotalClaims,
                COUNT(DISTINCT m.MemberID) AS MemberCount
            FROM Insurance.Members m
            JOIN Insurance.PolicyMembers pm ON m.MemberID = pm.MemberID
            JOIN Insurance.Policies p ON pm.PolicyID = p.PolicyID
            JOIN Insurance.CoveragePlans cp ON p.PlanID = cp.PlanID
            LEFT JOIN Insurance.PremiumPayments pp ON p.PolicyID = pp.PolicyID AND pp.PaymentDate BETWEEN ? AND ?
            LEFT JOIN Insurance.Claims c ON m.MemberID = c.MemberID AND c.ServiceDate BETWEEN ? AND ?
            WHERE p.Status = 'Active'
            GROUP BY 
                CASE 
                    WHEN DATEDIFF(YEAR, m.DateOfBirth, GETDATE()) < 18 THEN 'Under 18'
                    WHEN DATEDIFF(YEAR, m.DateOfBirth, GETDATE()) BETWEEN 18 AND 30 THEN '18-30'
                    WHEN DATEDIFF(YEAR, m.DateOfBirth, GETDATE()) BETWEEN 31 AND 50 THEN '31-50'
                    WHEN DATEDIFF(YEAR, m.DateOfBirth, GETDATE()) BETWEEN 51 AND 70 THEN '51-70'
                    ELSE '71+'
                END,
                m.Gender,
                m.State,
                CASE 
                    WHEN cp.HospitalTier = 'Gold' THEN 'Gold'
                    WHEN cp.HospitalTier = 'Silver' THEN 'Silver'
                    WHEN cp.HospitalTier = 'Bronze' THEN 'Bronze'
                    WHEN cp.HospitalTier = 'Basic' THEN 'Basic'
                    ELSE 'Other'
                END
            """
            return execute_query(query, (start_date, simulation_date, start_date, simulation_date))
        except Exception as e:
            print(f"Error getting aggregated data: {e}")
            return []
    
    def _generate_loss_ratio_metrics(self, aggregated_data: List[Dict[str, Any]], simulation_date: date) -> List[ActuarialMetric]:
        """Generate loss ratio metrics."""
        metrics = []
        
        for data in aggregated_data:
            total_premiums = data.get('TotalPremiums', 0) or 0
            total_claims = data.get('TotalClaims', 0) or 0
            
            # Skip if no premiums
            if total_premiums == 0:
                continue
            
            # Calculate loss ratio
            loss_ratio = total_claims / total_premiums if total_premiums > 0 else 0
            
            # Add some random variation
            loss_ratio += random.uniform(-0.05, 0.05)
            loss_ratio = max(0.0, min(1.5, loss_ratio))
            
            # Determine risk segment
            risk_segment = self._determine_risk_segment(loss_ratio)
            
            # Create metric
            metric = ActuarialMetric(
                metric_date=simulation_date,
                metric_type="Loss Ratio",
                metric_category="Hospital",
                metric_value=loss_ratio,
                age_group=data.get('AgeGroup'),
                gender=data.get('Gender'),
                state_territory=data.get('StateTerritory'),
                product_category=data.get('ProductCategory'),
                risk_segment=risk_segment
            )
            
            metrics.append(metric)
        
        return metrics
    
    def _generate_lapse_rate_metrics(self, aggregated_data: List[Dict[str, Any]], simulation_date: date) -> List[ActuarialMetric]:
        """Generate lapse rate metrics."""
        metrics = []
        
        for data in aggregated_data:
            # Generate a realistic lapse rate based on age group and product category
            base_lapse_rate = 0.1  # 10% base lapse rate
            
            # Adjust based on age group
            age_group = data.get('AgeGroup')
            if age_group == '18-30':
                base_lapse_rate += 0.05  # Higher for younger members
            elif age_group == '71+':
                base_lapse_rate -= 0.05  # Lower for older members
            
            # Adjust based on product category
            product_category = data.get('ProductCategory')
            if product_category == 'Gold':
                base_lapse_rate -= 0.03  # Lower for premium products
            elif product_category == 'Basic':
                base_lapse_rate += 0.03  # Higher for basic products
            
            # Add some random variation
            lapse_rate = base_lapse_rate + random.uniform(-0.02, 0.02)
            lapse_rate = max(0.01, min(0.3, lapse_rate))
            
            # Create metric
            metric = ActuarialMetric(
                metric_date=simulation_date,
                metric_type="Lapse Rate",
                metric_category="Hospital",
                metric_value=lapse_rate,
                age_group=data.get('AgeGroup'),
                gender=data.get('Gender'),
                state_territory=data.get('StateTerritory'),
                product_category=data.get('ProductCategory'),
                risk_segment=self._determine_risk_segment(lapse_rate, inverse=True)
            )
            
            metrics.append(metric)
        
        return metrics
    
    def _generate_acquisition_cost_metrics(self, aggregated_data: List[Dict[str, Any]], simulation_date: date) -> List[ActuarialMetric]:
        """Generate acquisition cost metrics."""
        metrics = []
        
        # Get unique combinations of age group and product category
        age_product_combinations = set()
        for data in aggregated_data:
            age_group = data.get('AgeGroup')
            product_category = data.get('ProductCategory')
            if age_group and product_category:
                age_product_combinations.add((age_group, product_category))
        
        for age_group, product_category in age_product_combinations:
            # Generate acquisition cost
            base_cost = 300  # Base acquisition cost
            
            # Adjust based on age group
            if age_group == '18-30':
                base_cost += 50  # Higher for younger members
            elif age_group == '71+':
                base_cost -= 50  # Lower for older members
            
            # Adjust based on product category
            if product_category == 'Gold':
                base_cost += 100  # Higher for premium products
            elif product_category == 'Basic':
                base_cost -= 100  # Lower for basic products
            
            # Add some random variation
            acquisition_cost = base_cost + random.uniform(-30, 30)
            acquisition_cost = max(100, acquisition_cost)
            
            # Create metric
            metric = ActuarialMetric(
                metric_date=simulation_date,
                metric_type="Acquisition Cost",
                metric_category="Hospital",
                metric_value=acquisition_cost,
                age_group=age_group,
                product_category=product_category
            )
            
            metrics.append(metric)
            
            # Also generate retention cost (typically lower than acquisition cost)
            retention_cost = acquisition_cost * random.uniform(0.2, 0.4)
            
            # Create retention cost metric
            metric = ActuarialMetric(
                metric_date=simulation_date,
                metric_type="Retention Cost",
                metric_category="Hospital",
                metric_value=retention_cost,
                age_group=age_group,
                product_category=product_category
            )
            
            metrics.append(metric)
        
        return metrics
    
    def _determine_risk_segment(self, value: float, inverse: bool = False) -> str:
        """
        Determine the risk segment based on a value.
        
        Args:
            value: The value to evaluate
            inverse: If True, lower values are higher risk
            
        Returns:
            Risk segment as a string
        """
        if inverse:
            if value < 0.05:
                return "Very Low"
            elif value < 0.1:
                return "Low"
            elif value < 0.15:
                return "Medium"
            elif value < 0.2:
                return "High"
            else:
                return "Very High"
        else:
            if value < 0.7:
                return "Very Low"
            elif value < 0.8:
                return "Low"
            elif value < 0.9:
                return "Medium"
            elif value < 1.0:
                return "High"
            else:
                return "Very High"