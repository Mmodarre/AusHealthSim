"""
Fraud pattern generator for enhanced simulation.
"""
from datetime import date, datetime, timedelta
import random
from typing import Dict, List, Any, Optional

from health_insurance_au.utils.db_utils import execute_query, execute_non_query, bulk_insert
from health_insurance_au.models.models import FraudIndicator, Claim

class FraudPatternGenerator:
    """Generator for fraud patterns in claims."""
    
    def __init__(self):
        """Initialize the fraud pattern generator."""
        self.fraud_indicators = self._load_fraud_indicators()
    
    def _load_fraud_indicators(self) -> List[FraudIndicator]:
        """Load fraud indicators from the database."""
        indicators = []
        try:
            results = execute_query("SELECT * FROM Insurance.FraudIndicators")
            for row in results:
                indicator = FraudIndicator(
                    indicator_id=row['IndicatorID'],
                    indicator_code=row['IndicatorCode'],
                    indicator_name=row['IndicatorName'],
                    indicator_description=row['IndicatorDescription'],
                    severity_level=row['SeverityLevel'],
                    detection_logic=row['DetectionLogic'],
                    created_date=row.get('CreatedDate'),
                    last_modified=row.get('LastModified')
                )
                indicators.append(indicator)
        except Exception as e:
            print(f"Error loading fraud indicators: {e}")
        
        return indicators
    
    def apply_fraud_patterns(self, simulation_date: date, fraud_rate: float = 0.05) -> Dict[str, int]:
        """
        Apply fraud patterns to claims.
        
        Args:
            simulation_date: The simulation date
            fraud_rate: The rate of fraudulent claims (0.0 to 1.0)
            
        Returns:
            Dictionary with statistics about updated claims
        """
        # Get recent claims
        claims = self._get_recent_claims(simulation_date)
        
        # Apply fraud patterns to a subset of claims
        fraud_count = int(len(claims) * fraud_rate)
        if fraud_count == 0 and len(claims) > 0:
            fraud_count = 1  # Ensure at least one fraud if there are claims
        
        fraud_claims = random.sample(claims, min(fraud_count, len(claims)))
        
        # Update the claims with fraud indicators
        updated_claims = []
        for claim in fraud_claims:
            # Choose a random fraud pattern
            pattern = random.choice(['duplicate_service', 'upcoding', 'unbundling', 'phantom_billing', 'unusual_modifier'])
            
            # Apply the pattern
            claim = self._apply_pattern(claim, pattern)
            updated_claims.append(claim)
        
        # Update the claims in the database
        self._update_claims(updated_claims, simulation_date)
        
        return {
            'claims_updated': len(updated_claims)
        }
    
    def _get_recent_claims(self, simulation_date: date) -> List[Dict[str, Any]]:
        """Get recent claims from the database."""
        try:
            # Get claims from the last 30 days
            start_date = simulation_date - timedelta(days=30)
            query = """
            SELECT * FROM Insurance.Claims 
            WHERE ServiceDate BETWEEN ? AND ?
            """
            return execute_query(query, (start_date, simulation_date))
        except Exception as e:
            print(f"Error getting recent claims: {e}")
            return []
    
    def _apply_pattern(self, claim: Dict[str, Any], pattern: str) -> Dict[str, Any]:
        """Apply a fraud pattern to a claim."""
        # Set base anomaly score
        anomaly_score = random.uniform(0.6, 0.95)
        
        # Set fraud indicator count
        fraud_indicator_count = random.randint(1, 3)
        
        # Set unusual pattern flag
        unusual_pattern_flag = True
        
        # Set claim complexity score
        claim_complexity_score = random.uniform(2.0, 5.0)
        
        # Set claim adjustment history
        adjustment_history = f"Potential {pattern} detected on {datetime.now().strftime('%Y-%m-%d')}"
        
        # Set review flag
        review_flag = True
        
        # Update the claim
        claim['AnomalyScore'] = anomaly_score
        claim['FraudIndicatorCount'] = fraud_indicator_count
        claim['UnusualPatternFlag'] = unusual_pattern_flag
        claim['ClaimComplexityScore'] = claim_complexity_score
        claim['ClaimAdjustmentHistory'] = adjustment_history
        claim['ReviewFlag'] = review_flag
        
        return claim
    
    def _update_claims(self, claims: List[Dict[str, Any]], simulation_date: date) -> None:
        """Update claims in the database."""
        for claim in claims:
            try:
                query = """
                UPDATE Insurance.Claims
                SET AnomalyScore = ?,
                    FraudIndicatorCount = ?,
                    UnusualPatternFlag = ?,
                    ClaimComplexityScore = ?,
                    ClaimAdjustmentHistory = ?,
                    ReviewFlag = ?,
                    LastModified = ?
                WHERE ClaimID = ?
                """
                execute_non_query(query, (
                    claim['AnomalyScore'],
                    claim['FraudIndicatorCount'],
                    claim['UnusualPatternFlag'],
                    claim['ClaimComplexityScore'],
                    claim['ClaimAdjustmentHistory'],
                    claim['ReviewFlag'],
                    simulation_date,
                    claim['ClaimID']
                ))
            except Exception as e:
                print(f"Error updating claim {claim['ClaimID']}: {e}")