"""
Fraud pattern generation module for the Health Insurance AU simulation.
"""
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from health_insurance_au.models.models import Claim, FraudIndicator, ClaimPattern
from health_insurance_au.utils.db_utils import execute_query, bulk_insert
from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

class FraudPatternGenerator:
    """
    Class for generating realistic fraud-like patterns in claims data.
    """
    
    def __init__(self, anomaly_frequency: float = 0.05):
        """
        Initialize the fraud pattern generator.
        
        Args:
            anomaly_frequency: Frequency of anomalies to generate (0.0 to 1.0)
        """
        self.anomaly_frequency = anomaly_frequency
        self.fraud_indicators = self._load_fraud_indicators()
        
    def _load_fraud_indicators(self) -> List[FraudIndicator]:
        """
        Load fraud indicators from the database.
        
        Returns:
            A list of FraudIndicator objects
        """
        try:
            indicators_data = execute_query("SELECT * FROM Insurance.FraudIndicators")
            indicators = []
            
            for data in indicators_data:
                indicator = FraudIndicator(
                    indicator_id=data['IndicatorID'],
                    indicator_code=data['IndicatorCode'],
                    indicator_name=data['IndicatorName'],
                    indicator_description=data['IndicatorDescription'],
                    severity_level=data['SeverityLevel'],
                    detection_logic=data['DetectionLogic'],
                    created_date=data['CreatedDate'],
                    last_modified=data['LastModified']
                )
                indicators.append(indicator)
            
            logger.info(f"Loaded {len(indicators)} fraud indicators from database")
            return indicators
        except Exception as e:
            logger.error(f"Error loading fraud indicators: {e}")
            return []
    
    def apply_fraud_patterns_to_claims(self, claims: List[Claim], simulation_date: date = None) -> List[Claim]:
        """
        Apply fraud patterns to a list of claims.
        
        Args:
            claims: List of claims to apply patterns to
            simulation_date: The simulation date
            
        Returns:
            The updated list of claims with fraud patterns applied
        """
        if not claims:
            return claims
            
        if simulation_date is None:
            simulation_date = date.today()
        
        # Determine how many claims should have anomalies
        anomaly_count = max(1, int(len(claims) * self.anomaly_frequency))
        
        # Select random claims to apply anomalies to
        anomaly_claims = random.sample(claims, anomaly_count)
        
        for claim in anomaly_claims:
            # Apply random anomaly pattern
            self._apply_random_anomaly(claim)
        
        logger.info(f"Applied fraud patterns to {anomaly_count} claims")
        return claims
    
    def _apply_random_anomaly(self, claim: Claim) -> None:
        """
        Apply a random anomaly pattern to a claim.
        
        Args:
            claim: The claim to apply the anomaly to
        """
        anomaly_type = random.choice([
            'duplicate_service',
            'upcoding',
            'unbundling',
            'phantom_billing',
            'unusual_modifier'
        ])
        
        if anomaly_type == 'duplicate_service':
            claim.anomaly_score = random.uniform(0.7, 0.95)
            claim.fraud_indicator_count = random.randint(1, 3)
            claim.unusual_pattern_flag = True
            claim.claim_complexity_score = random.uniform(0.1, 0.3)
            claim.review_flag = True
        
        elif anomaly_type == 'upcoding':
            claim.anomaly_score = random.uniform(0.6, 0.85)
            claim.fraud_indicator_count = random.randint(1, 2)
            claim.unusual_pattern_flag = True
            claim.claim_complexity_score = random.uniform(0.4, 0.7)
            claim.review_flag = random.random() < 0.8
        
        elif anomaly_type == 'unbundling':
            claim.anomaly_score = random.uniform(0.5, 0.8)
            claim.fraud_indicator_count = random.randint(1, 4)
            claim.unusual_pattern_flag = True
            claim.claim_complexity_score = random.uniform(0.6, 0.9)
            claim.review_flag = random.random() < 0.7
        
        elif anomaly_type == 'phantom_billing':
            claim.anomaly_score = random.uniform(0.8, 0.98)
            claim.fraud_indicator_count = random.randint(2, 5)
            claim.unusual_pattern_flag = True
            claim.claim_complexity_score = random.uniform(0.2, 0.5)
            claim.review_flag = True
        
        elif anomaly_type == 'unusual_modifier':
            claim.anomaly_score = random.uniform(0.4, 0.7)
            claim.fraud_indicator_count = random.randint(1, 2)
            claim.unusual_pattern_flag = random.random() < 0.6
            claim.claim_complexity_score = random.uniform(0.3, 0.6)
            claim.review_flag = random.random() < 0.5
    
    def generate_claim_patterns(self, members: List[int], providers: List[int], simulation_date: date = None) -> List[ClaimPattern]:
        """
        Generate claim patterns for detection.
        
        Args:
            members: List of member IDs
            providers: List of provider IDs
            simulation_date: The simulation date
            
        Returns:
            A list of generated ClaimPattern objects
        """
        if simulation_date is None:
            simulation_date = date.today()
        
        patterns = []
        pattern_count = random.randint(3, 10)  # Generate a few patterns
        
        pattern_types = [
            'Frequent Small Claims',
            'High Value Services',
            'Weekend Services',
            'Multiple Daily Visits',
            'Service Unbundling',
            'Distant Patient Services'
        ]
        
        for _ in range(pattern_count):
            member_id = random.choice(members)
            provider_id = random.choice(providers)
            pattern_type = random.choice(pattern_types)
            
            first_detected = simulation_date - timedelta(days=random.randint(30, 180))
            last_detected = first_detected + timedelta(days=random.randint(1, 30))
            
            pattern = ClaimPattern(
                member_id=member_id,
                provider_id=provider_id,
                pattern_type=pattern_type,
                pattern_description=f"{pattern_type} pattern detected between member {member_id} and provider {provider_id}",
                first_detected_date=first_detected,
                last_detected_date=last_detected,
                occurrence_count=random.randint(3, 15),
                average_amount=random.uniform(100.0, 1500.0),
                confidence_score=random.uniform(0.5, 0.95),
                status=random.choice(['Active', 'Monitoring', 'Resolved', 'False Positive']),
                created_date=datetime.combine(simulation_date, datetime.min.time()),
                last_modified=datetime.combine(simulation_date, datetime.min.time())
            )
            
            patterns.append(pattern)
        
        logger.info(f"Generated {len(patterns)} claim patterns")
        return patterns
    
    def save_claim_patterns(self, patterns: List[ClaimPattern], simulation_date: date = None) -> int:
        """
        Save claim patterns to the database.
        
        Args:
            patterns: List of claim patterns to save
            simulation_date: The simulation date
            
        Returns:
            Number of patterns saved
        """
        if not patterns:
            return 0
            
        if simulation_date is None:
            simulation_date = date.today()
        
        pattern_dicts = [pattern.to_dict() for pattern in patterns]
        
        try:
            rows_affected = bulk_insert("Insurance.ClaimPatterns", pattern_dicts, simulation_date)
            logger.info(f"Saved {rows_affected} claim patterns to database")
            return rows_affected
        except Exception as e:
            logger.error(f"Error saving claim patterns: {e}")
            return 0