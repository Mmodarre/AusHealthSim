"""
Unit tests for enhanced data models.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime

from health_insurance_au.models.models import (
    Member, Policy, Claim, Provider, 
    FraudIndicator, FinancialTransaction, ActuarialMetric, ClaimPattern
)

class TestEnhancedModels(unittest.TestCase):
    """Test cases for enhanced data models."""
    
    def test_member_with_risk_profile(self):
        """Test Member class with risk profile attributes."""
        member = Member(
            first_name="John",
            last_name="Smith",
            date_of_birth=date(1980, 1, 1),
            gender="M",
            address_line1="123 Main St",
            city="Sydney",
            state="NSW",
            post_code="2000",
            country="Australia",
            member_number="M123456",
            join_date=date(2020, 1, 1),
            is_active=True,
            risk_score=75.5,
            chronic_condition_flag=True,
            lifestyle_risk_factor="Sedentary",
            claim_frequency_tier="High",
            predicted_churn=0.25
        )
        
        # Verify basic attributes
        self.assertEqual(member.member_number, "M123456")
        self.assertEqual(member.first_name, "John")
        
        # Verify enhanced attributes
        self.assertEqual(member.risk_score, 75.5)
        self.assertTrue(member.chronic_condition_flag)
        self.assertEqual(member.lifestyle_risk_factor, "Sedentary")
        self.assertEqual(member.claim_frequency_tier, "High")
        self.assertEqual(member.predicted_churn, 0.25)
        
        # Test to_dict method includes enhanced attributes
        member_dict = member.to_dict()
        self.assertEqual(member_dict['RiskScore'], 75.5)
        self.assertEqual(member_dict['ChronicConditionFlag'], True)
        self.assertEqual(member_dict['LifestyleRiskFactor'], "Sedentary")
        self.assertEqual(member_dict['ClaimFrequencyTier'], "High")
        self.assertEqual(member_dict['PredictedChurn'], 0.25)
    
    def test_policy_with_risk_attributes(self):
        """Test Policy class with risk attributes."""
        policy = Policy(
            policy_number="P123456",
            primary_member_id=1,
            plan_id=1,
            coverage_type="Hospital",
            start_date=date(2020, 1, 1),
            current_premium=200.0,
            status="Active",
            apra_entity_code="ABC123",
            risk_adjusted_loading=1.25,
            underwriting_score=85.0,
            policy_value_segment="High",
            retention_risk_score=0.15
        )
        
        # Verify basic attributes
        self.assertEqual(policy.policy_number, "P123456")
        self.assertEqual(policy.coverage_type, "Hospital")
        
        # Verify enhanced attributes
        self.assertEqual(policy.apra_entity_code, "ABC123")
        self.assertEqual(policy.risk_adjusted_loading, 1.25)
        self.assertEqual(policy.underwriting_score, 85.0)
        self.assertEqual(policy.policy_value_segment, "High")
        self.assertEqual(policy.retention_risk_score, 0.15)
        
        # Test to_dict method includes enhanced attributes
        policy_dict = policy.to_dict()
        self.assertEqual(policy_dict['APRAEntityCode'], "ABC123")
        self.assertEqual(policy_dict['RiskAdjustedLoading'], 1.25)
        self.assertEqual(policy_dict['UnderwritingScore'], 85.0)
        self.assertEqual(policy_dict['PolicyValueSegment'], "High")
        self.assertEqual(policy_dict['RetentionRiskScore'], 0.15)
    
    def test_claim_with_fraud_attributes(self):
        """Test Claim class with fraud detection attributes."""
        claim = Claim(
            claim_number="C123456",
            policy_id=1,
            member_id=1,
            provider_id=1,
            service_date=datetime(2020, 1, 1),
            submission_date=datetime(2020, 1, 5),
            claim_type="Hospital",
            service_description="Appendectomy",
            charged_amount=1000.0,
            medicare_amount=500.0,
            insurance_amount=400.0,
            gap_amount=100.0,
            status="Submitted",
            anomaly_score=0.85,
            fraud_indicator_count=2,
            unusual_pattern_flag=True,
            claim_complexity_score=3.5,
            claim_adjustment_history="Adjusted due to incorrect code",
            review_flag=True
        )
        
        # Verify basic attributes
        self.assertEqual(claim.claim_number, "C123456")
        self.assertEqual(claim.service_description, "Appendectomy")
        
        # Verify enhanced attributes
        self.assertEqual(claim.anomaly_score, 0.85)
        self.assertEqual(claim.fraud_indicator_count, 2)
        self.assertTrue(claim.unusual_pattern_flag)
        self.assertEqual(claim.claim_complexity_score, 3.5)
        self.assertEqual(claim.claim_adjustment_history, "Adjusted due to incorrect code")
        self.assertTrue(claim.review_flag)
        
        # Test to_dict method includes enhanced attributes
        claim_dict = claim.to_dict()
        self.assertEqual(claim_dict['AnomalyScore'], 0.85)
        self.assertEqual(claim_dict['FraudIndicatorCount'], 2)
        self.assertEqual(claim_dict['UnusualPatternFlag'], True)
        self.assertEqual(claim_dict['ClaimComplexityScore'], 3.5)
        self.assertEqual(claim_dict['ClaimAdjustmentHistory'], "Adjusted due to incorrect code")
        self.assertEqual(claim_dict['ReviewFlag'], True)
    
    def test_provider_with_billing_attributes(self):
        """Test Provider class with billing pattern attributes."""
        provider = Provider(
            provider_number="PR123456",
            provider_name="Sydney Medical Center",
            provider_type="Hospital",
            address_line1="456 Health St",
            city="Sydney",
            state="NSW",
            post_code="2000",
            country="Australia",
            billing_pattern_score=0.65,
            avg_claim_value=750.0,
            claim_frequency_rating="Medium",
            specialty_risk_factor=1.2,
            compliance_score=0.85
        )
        
        # Verify basic attributes
        self.assertEqual(provider.provider_number, "PR123456")
        self.assertEqual(provider.provider_name, "Sydney Medical Center")
        
        # Verify enhanced attributes
        self.assertEqual(provider.billing_pattern_score, 0.65)
        self.assertEqual(provider.avg_claim_value, 750.0)
        self.assertEqual(provider.claim_frequency_rating, "Medium")
        self.assertEqual(provider.specialty_risk_factor, 1.2)
        self.assertEqual(provider.compliance_score, 0.85)
        
        # Test to_dict method includes enhanced attributes
        provider_dict = provider.to_dict()
        self.assertEqual(provider_dict['BillingPatternScore'], 0.65)
        self.assertEqual(provider_dict['AvgClaimValue'], 750.0)
        self.assertEqual(provider_dict['ClaimFrequencyRating'], "Medium")
        self.assertEqual(provider_dict['SpecialtyRiskFactor'], 1.2)
        self.assertEqual(provider_dict['ComplianceScore'], 0.85)
    
    def test_fraud_indicator(self):
        """Test FraudIndicator class."""
        indicator = FraudIndicator(
            indicator_code="DUP_CLAIM",
            indicator_name="Duplicate Claim",
            indicator_description="Multiple claims for the same service on the same date",
            severity_level="High",
            detection_logic="Claims with identical service dates, service descriptions, and member IDs within a 30-day period",
            indicator_id=1,
            created_date=datetime(2023, 1, 1),
            last_modified=datetime(2023, 1, 1)
        )
        
        self.assertEqual(indicator.indicator_id, 1)
        self.assertEqual(indicator.indicator_code, "DUP_CLAIM")
        self.assertEqual(indicator.indicator_name, "Duplicate Claim")
        self.assertEqual(indicator.severity_level, "High")
        
        # Test to_dict method
        indicator_dict = indicator.to_dict()
        self.assertEqual(indicator_dict['IndicatorCode'], "DUP_CLAIM")
        self.assertEqual(indicator_dict['IndicatorName'], "Duplicate Claim")
        self.assertEqual(indicator_dict['SeverityLevel'], "High")
    
    def test_financial_transaction(self):
        """Test FinancialTransaction class."""
        transaction = FinancialTransaction(
            transaction_type="Premium Payment",
            transaction_date=date(2023, 1, 1),
            amount=200.0,
            description="Monthly premium payment",
            reference_number="PMT-20230101-12345",
            related_entity_type="Policy",
            related_entity_id=1,
            processed_date=datetime(2023, 1, 1, 10, 30),
            status="Successful",
            created_by="System",
            transaction_id=1,
            created_date=datetime(2023, 1, 1),
            last_modified=datetime(2023, 1, 1)
        )
        
        self.assertEqual(transaction.transaction_id, 1)
        self.assertEqual(transaction.transaction_type, "Premium Payment")
        self.assertEqual(transaction.amount, 200.0)
        self.assertEqual(transaction.reference_number, "PMT-20230101-12345")
        self.assertEqual(transaction.related_entity_type, "Policy")
        self.assertEqual(transaction.related_entity_id, 1)
        
        # Test to_dict method
        transaction_dict = transaction.to_dict()
        self.assertEqual(transaction_dict['TransactionType'], "Premium Payment")
        self.assertEqual(transaction_dict['Amount'], 200.0)
        self.assertEqual(transaction_dict['ReferenceNumber'], "PMT-20230101-12345")
        self.assertEqual(transaction_dict['RelatedEntityType'], "Policy")
        self.assertEqual(transaction_dict['RelatedEntityID'], 1)
    
    def test_actuarial_metric(self):
        """Test ActuarialMetric class."""
        metric = ActuarialMetric(
            metric_date=date(2023, 1, 1),
            metric_type="Loss Ratio",
            metric_category="Hospital",
            metric_value=0.82,
            metric_id=1,
            age_group="18-30",
            gender="M",
            state_territory="NSW",
            product_category="Gold",
            risk_segment="Low",
            created_date=datetime(2023, 1, 1),
            last_modified=datetime(2023, 1, 1)
        )
        
        self.assertEqual(metric.metric_id, 1)
        self.assertEqual(metric.metric_type, "Loss Ratio")
        self.assertEqual(metric.metric_category, "Hospital")
        self.assertEqual(metric.metric_value, 0.82)
        self.assertEqual(metric.age_group, "18-30")
        self.assertEqual(metric.gender, "M")
        
        # Test to_dict method
        metric_dict = metric.to_dict()
        self.assertEqual(metric_dict['MetricType'], "Loss Ratio")
        self.assertEqual(metric_dict['MetricCategory'], "Hospital")
        self.assertEqual(metric_dict['MetricValue'], 0.82)
        self.assertEqual(metric_dict['AgeGroup'], "18-30")
        self.assertEqual(metric_dict['Gender'], "M")
    
    def test_claim_pattern(self):
        """Test ClaimPattern class."""
        pattern = ClaimPattern(
            member_id=1,
            provider_id=1,
            pattern_type="High Frequency",
            pattern_description="Multiple claims in short period",
            first_detected_date=date(2023, 1, 1),
            last_detected_date=date(2023, 1, 15),
            occurrence_count=5,
            average_amount=150.0,
            confidence_score=0.85,
            status="Active",
            pattern_id=1,
            created_date=datetime(2023, 1, 1),
            last_modified=datetime(2023, 1, 1)
        )
        
        self.assertEqual(pattern.pattern_id, 1)
        self.assertEqual(pattern.member_id, 1)
        self.assertEqual(pattern.provider_id, 1)
        self.assertEqual(pattern.pattern_type, "High Frequency")
        self.assertEqual(pattern.occurrence_count, 5)
        self.assertEqual(pattern.average_amount, 150.0)
        self.assertEqual(pattern.confidence_score, 0.85)
        
        # Test to_dict method
        pattern_dict = pattern.to_dict()
        self.assertEqual(pattern_dict['MemberID'], 1)
        self.assertEqual(pattern_dict['ProviderID'], 1)
        self.assertEqual(pattern_dict['PatternType'], "High Frequency")
        self.assertEqual(pattern_dict['OccurrenceCount'], 5)
        self.assertEqual(pattern_dict['AverageAmount'], 150.0)
        self.assertEqual(pattern_dict['ConfidenceScore'], 0.85)

if __name__ == '__main__':
    unittest.main()