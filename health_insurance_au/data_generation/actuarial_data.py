"""
Actuarial data generation module for the Health Insurance AU simulation.
"""
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from health_insurance_au.models.models import ActuarialMetric
from health_insurance_au.utils.db_utils import execute_query, bulk_insert
from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

class ActuarialDataGenerator:
    """
    Class for generating actuarial metrics and cost data.
    """
    
    def __init__(self):
        """Initialize the actuarial data generator."""
        # Define metric types and their characteristics
        self.metric_types = {
            'Loss Ratio': {
                'value_range': (0.6, 1.1),
                'trend_factor': 0.01,  # Annual trend
                'seasonality': {
                    1: 0.02,   # January: higher
                    2: 0.01,   # February
                    3: 0.0,    # March
                    4: -0.01,  # April
                    5: -0.02,  # May
                    6: -0.03,  # June: lower (end of financial year)
                    7: 0.03,   # July: higher (start of financial year)
                    8: 0.02,   # August
                    9: 0.01,   # September
                    10: 0.0,   # October
                    11: -0.01, # November
                    12: 0.02   # December: higher
                }
            },
            'Lapse Rate': {
                'value_range': (0.05, 0.2),
                'trend_factor': 0.005,
                'seasonality': {
                    1: 0.03,   # January: higher
                    2: 0.02,   # February
                    3: 0.01,   # March
                    4: 0.0,    # April
                    5: -0.01,  # May
                    6: -0.02,  # June
                    7: 0.04,   # July: higher (price changes)
                    8: 0.02,   # August
                    9: 0.0,    # September
                    10: -0.01, # October
                    11: -0.02, # November
                    12: -0.01  # December
                }
            },
            'Acquisition Cost': {
                'value_range': (150.0, 400.0),
                'trend_factor': 10.0,  # Annual increase
                'seasonality': {
                    1: 0.05,   # January: higher
                    2: 0.03,   # February
                    3: 0.01,   # March
                    4: 0.0,    # April
                    5: -0.01,  # May
                    6: 0.03,   # June: higher (end of financial year)
                    7: -0.02,  # July
                    8: -0.01,  # August
                    9: 0.0,    # September
                    10: 0.01,  # October
                    11: 0.02,  # November
                    12: 0.03   # December: higher
                }
            },
            'Retention Cost': {
                'value_range': (50.0, 120.0),
                'trend_factor': 5.0,
                'seasonality': {
                    1: 0.01,   # January
                    2: 0.0,    # February
                    3: 0.0,    # March
                    4: 0.01,   # April
                    5: 0.02,   # May
                    6: 0.03,   # June: higher (end of financial year)
                    7: -0.01,  # July
                    8: -0.01,  # August
                    9: 0.0,    # September
                    10: 0.0,   # October
                    11: 0.01,  # November
                    12: 0.02   # December
                }
            },
            'Claims Frequency': {
                'value_range': (1.5, 4.0),
                'trend_factor': 0.1,
                'seasonality': {
                    1: 0.0,    # January
                    2: 0.01,   # February
                    3: 0.02,   # March
                    4: 0.03,   # April
                    5: 0.04,   # May
                    6: 0.05,   # June: higher (end of financial year)
                    7: -0.02,  # July
                    8: -0.01,  # August
                    9: 0.0,    # September
                    10: 0.01,  # October
                    11: 0.02,  # November
                    12: 0.03   # December
                }
            }
        }
        
        # Define categories
        self.categories = {
            'Hospital': ['Basic', 'Bronze', 'Silver', 'Gold'],
            'Extras': ['Basic', 'Medium', 'Top'],
            'Combined': ['Basic', 'Bronze', 'Silver', 'Gold']
        }
        
        # Define age groups
        self.age_groups = ['18-30', '31-50', '51-70', '71+']
        
        # Define genders
        self.genders = ['M', 'F']
        
        # Define states/territories
        self.states = ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT']
        
        # Define risk segments
        self.risk_segments = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
    
    def generate_monthly_metrics(self, metric_date: date, num_metrics: int = 100) -> List[ActuarialMetric]:
        """
        Generate monthly actuarial metrics.
        
        Args:
            metric_date: The date for the metrics
            num_metrics: Number of metrics to generate
            
        Returns:
            A list of ActuarialMetric objects
        """
        metrics = []
        
        # Calculate years since 2020 for trend calculation
        years_since_base = (metric_date.year - 2020) + (metric_date.month / 12.0)
        
        for _ in range(num_metrics):
            # Select random attributes
            metric_type = random.choice(list(self.metric_types.keys()))
            category_type = random.choice(list(self.categories.keys()))
            product_category = random.choice(self.categories[category_type])
            
            # Decide whether to include demographic breakdowns
            include_demographics = random.random() < 0.7  # 70% chance
            
            if include_demographics:
                age_group = random.choice(self.age_groups)
                gender = random.choice(self.genders)
                state = random.choice(self.states)
                risk_segment = random.choice(self.risk_segments)
            else:
                age_group = None
                gender = None
                state = None
                risk_segment = None
            
            # Get base value range and apply trends and seasonality
            min_value, max_value = self.metric_types[metric_type]['value_range']
            trend = self.metric_types[metric_type]['trend_factor'] * years_since_base
            seasonality = self.metric_types[metric_type]['seasonality'].get(metric_date.month, 0.0)
            
            # Adjust range based on trend and seasonality
            adjusted_min = min_value * (1 + trend + seasonality)
            adjusted_max = max_value * (1 + trend + seasonality)
            
            # Further adjust based on product category
            if product_category == 'Gold':
                category_factor = 1.2
            elif product_category == 'Silver':
                category_factor = 1.1
            elif product_category == 'Bronze':
                category_factor = 1.0
            else:  # Basic
                category_factor = 0.9
                
            adjusted_min *= category_factor
            adjusted_max *= category_factor
            
            # Generate the value
            metric_value = round(random.uniform(adjusted_min, adjusted_max), 4)
            
            # Create the metric
            metric = ActuarialMetric(
                metric_date=metric_date,
                metric_type=metric_type,
                metric_category=category_type,
                metric_value=metric_value,
                age_group=age_group,
                gender=gender,
                state_territory=state,
                product_category=product_category,
                risk_segment=risk_segment
            )
            
            metrics.append(metric)
        
        logger.info(f"Generated {len(metrics)} actuarial metrics for {metric_date}")
        return metrics
    
    def save_metrics(self, metrics: List[ActuarialMetric], simulation_date: date = None) -> int:
        """
        Save actuarial metrics to the database.
        
        Args:
            metrics: List of metrics to save
            simulation_date: The simulation date
            
        Returns:
            Number of metrics saved
        """
        if not metrics:
            return 0
            
        if simulation_date is None:
            simulation_date = date.today()
        
        metric_dicts = [metric.to_dict() for metric in metrics]
        
        try:
            rows_affected = bulk_insert("Insurance.ActuarialMetrics", metric_dicts, simulation_date)
            logger.info(f"Saved {rows_affected} actuarial metrics to database")
            return rows_affected
        except Exception as e:
            logger.error(f"Error saving actuarial metrics: {e}")
            return 0
    
    def generate_historical_metrics(self, start_date: date, end_date: date, metrics_per_month: int = 50) -> List[ActuarialMetric]:
        """
        Generate historical actuarial metrics over a date range.
        
        Args:
            start_date: The start date
            end_date: The end date
            metrics_per_month: Number of metrics to generate per month
            
        Returns:
            A list of ActuarialMetric objects
        """
        all_metrics = []
        
        # Generate metrics for each month in the range
        current_date = date(start_date.year, start_date.month, 1)  # Start at first of the month
        
        while current_date <= end_date:
            monthly_metrics = self.generate_monthly_metrics(current_date, metrics_per_month)
            all_metrics.extend(monthly_metrics)
            
            # Move to next month
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
        
        logger.info(f"Generated {len(all_metrics)} historical actuarial metrics from {start_date} to {end_date}")
        return all_metrics