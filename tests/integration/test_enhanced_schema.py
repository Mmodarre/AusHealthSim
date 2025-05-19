"""
Integration tests for enhanced database schema.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
import os

from health_insurance_au.utils.db_utils import execute_query, execute_non_query, bulk_insert
from health_insurance_au.models.models import (
    FraudIndicator, FinancialTransaction, ActuarialMetric, ClaimPattern
)

@unittest.skipIf(os.environ.get('SKIP_DB_TESTS') == 'true', "Skipping database tests")
class TestEnhancedSchemaIntegration(unittest.TestCase):
    """Integration tests for enhanced database schema."""
    
    def setUp(self):
        """Set up test environment."""
        # Check if the enhanced tables exist
        try:
            result = execute_query("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'FraudIndicators' AND TABLE_SCHEMA = 'Insurance'")
            self.enhanced_schema_exists = result and result[0][0] > 0
            if not self.enhanced_schema_exists:
                self.skipTest("Enhanced schema not available. Run initialize_db.sh --include-enhanced first.")
        except Exception as e:
            self.skipTest(f"Could not connect to database: {e}")
    
    def test_fraud_indicators_table(self):
        """Test that the FraudIndicators table exists and can be queried."""
        if not self.enhanced_schema_exists:
            self.skipTest("Enhanced schema not available")
        
        # Insert a test fraud indicator
        indicator = FraudIndicator(
            indicator_code="TEST_FRAUD",
            indicator_name="Test Fraud Indicator",
            indicator_description="Test fraud indicator for integration testing",
            severity_level="Medium",
            detection_logic="Test detection logic"
        )
        
        try:
            # Insert the indicator
            rows_affected = bulk_insert("Insurance.FraudIndicators", [indicator.to_dict()])
            self.assertEqual(rows_affected, 1)
            
            # Query the indicator
            result = execute_query("SELECT TOP 1 * FROM Insurance.FraudIndicators WHERE IndicatorCode = 'TEST_FRAUD'")
            self.assertTrue(result and len(result) > 0)
            self.assertEqual(result[0]['IndicatorCode'], "TEST_FRAUD")
            self.assertEqual(result[0]['IndicatorName'], "Test Fraud Indicator")
            self.assertEqual(result[0]['SeverityLevel'], "Medium")
            
            # Clean up
            execute_non_query("DELETE FROM Insurance.FraudIndicators WHERE IndicatorCode = 'TEST_FRAUD'")
        except Exception as e:
            self.fail(f"Error testing FraudIndicators table: {e}")
    
    def test_financial_transactions_table(self):
        """Test that the FinancialTransactions table exists and can be queried."""
        if not self.enhanced_schema_exists:
            self.skipTest("Enhanced schema not available")
        
        # Insert a test financial transaction
        transaction = FinancialTransaction(
            transaction_type="TEST_TRANSACTION",
            transaction_date=date.today(),
            amount=100.0,
            description="Test financial transaction",
            reference_number="TEST-REF-123",
            related_entity_type="Test",
            related_entity_id=1,
            processed_date=datetime.now(),
            status="Test",
            created_by="Integration Test"
        )
        
        try:
            # Insert the transaction
            rows_affected = bulk_insert("Insurance.FinancialTransactions", [transaction.to_dict()])
            self.assertEqual(rows_affected, 1)
            
            # Query the transaction
            result = execute_query("SELECT TOP 1 * FROM Insurance.FinancialTransactions WHERE ReferenceNumber = 'TEST-REF-123'")
            self.assertTrue(result and len(result) > 0)
            self.assertEqual(result[0]['TransactionType'], "TEST_TRANSACTION")
            self.assertEqual(result[0]['Amount'], 100.0)
            self.assertEqual(result[0]['ReferenceNumber'], "TEST-REF-123")
            
            # Clean up
            execute_non_query("DELETE FROM Insurance.FinancialTransactions WHERE ReferenceNumber = 'TEST-REF-123'")
        except Exception as e:
            self.fail(f"Error testing FinancialTransactions table: {e}")
    
    def test_actuarial_metrics_table(self):
        """Test that the ActuarialMetrics table exists and can be queried."""
        if not self.enhanced_schema_exists:
            self.skipTest("Enhanced schema not available")
        
        # Insert a test actuarial metric
        metric = ActuarialMetric(
            metric_date=date.today(),
            metric_type="TEST_METRIC",
            metric_category="Test",
            metric_value=0.95,
            age_group="Test",
            gender="T",
            state_territory="TST",
            product_category="Test",
            risk_segment="Test"
        )
        
        try:
            # Insert the metric
            rows_affected = bulk_insert("Insurance.ActuarialMetrics", [metric.to_dict()])
            self.assertEqual(rows_affected, 1)
            
            # Query the metric
            result = execute_query("SELECT TOP 1 * FROM Insurance.ActuarialMetrics WHERE MetricType = 'TEST_METRIC'")
            self.assertTrue(result and len(result) > 0)
            self.assertEqual(result[0]['MetricType'], "TEST_METRIC")
            self.assertEqual(result[0]['MetricCategory'], "Test")
            self.assertEqual(result[0]['MetricValue'], 0.95)
            
            # Clean up
            execute_non_query("DELETE FROM Insurance.ActuarialMetrics WHERE MetricType = 'TEST_METRIC'")
        except Exception as e:
            self.fail(f"Error testing ActuarialMetrics table: {e}")
    
    def test_claim_patterns_table(self):
        """Test that the ClaimPatterns table exists and can be queried."""
        if not self.enhanced_schema_exists:
            self.skipTest("Enhanced schema not available")
        
        # First, we need to make sure we have a member and provider to reference
        try:
            # Check if we have a member
            member_result = execute_query("SELECT TOP 1 MemberID FROM Insurance.Members")
            if not member_result:
                self.skipTest("No members available for testing")
            member_id = member_result[0]['MemberID']
            
            # Check if we have a provider
            provider_result = execute_query("SELECT TOP 1 ProviderID FROM Insurance.Providers")
            if not provider_result:
                self.skipTest("No providers available for testing")
            provider_id = provider_result[0]['ProviderID']
            
            # Insert a test claim pattern
            pattern = ClaimPattern(
                member_id=member_id,
                provider_id=provider_id,
                pattern_type="TEST_PATTERN",
                pattern_description="Test claim pattern",
                first_detected_date=date.today(),
                last_detected_date=date.today(),
                occurrence_count=3,
                average_amount=150.0,
                confidence_score=0.75,
                status="Test"
            )
            
            # Insert the pattern
            rows_affected = bulk_insert("Insurance.ClaimPatterns", [pattern.to_dict()])
            self.assertEqual(rows_affected, 1)
            
            # Query the pattern
            result = execute_query("SELECT TOP 1 * FROM Insurance.ClaimPatterns WHERE PatternType = 'TEST_PATTERN'")
            self.assertTrue(result and len(result) > 0)
            self.assertEqual(result[0]['PatternType'], "TEST_PATTERN")
            self.assertEqual(result[0]['PatternDescription'], "Test claim pattern")
            self.assertEqual(result[0]['OccurrenceCount'], 3)
            self.assertEqual(result[0]['AverageAmount'], 150.0)
            self.assertEqual(result[0]['ConfidenceScore'], 0.75)
            
            # Clean up
            execute_non_query("DELETE FROM Insurance.ClaimPatterns WHERE PatternType = 'TEST_PATTERN'")
        except Exception as e:
            self.fail(f"Error testing ClaimPatterns table: {e}")
    
    def test_member_enhanced_fields(self):
        """Test that the Member table has enhanced fields."""
        if not self.enhanced_schema_exists:
            self.skipTest("Enhanced schema not available")
        
        try:
            # Check if the enhanced columns exist
            columns = execute_query("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'Insurance' AND TABLE_NAME = 'Members' AND COLUMN_NAME IN 
                ('RiskScore', 'ChronicConditionFlag', 'LifestyleRiskFactor', 'ClaimFrequencyTier', 'PredictedChurn')
            """)
            
            # We should have 5 enhanced columns
            self.assertEqual(len(columns), 5)
            
            # Check if we can update these columns
            member_result = execute_query("SELECT TOP 1 MemberID FROM Insurance.Members")
            if not member_result:
                self.skipTest("No members available for testing")
            member_id = member_result[0]['MemberID']
            
            # Update the member with enhanced fields
            execute_non_query("""
                UPDATE Insurance.Members 
                SET RiskScore = 75.5, 
                    ChronicConditionFlag = 1, 
                    LifestyleRiskFactor = 'Test', 
                    ClaimFrequencyTier = 'Test', 
                    PredictedChurn = 0.25 
                WHERE MemberID = ?
            """, (member_id,))
            
            # Query the member
            result = execute_query("SELECT RiskScore, ChronicConditionFlag, LifestyleRiskFactor, ClaimFrequencyTier, PredictedChurn FROM Insurance.Members WHERE MemberID = ?", (member_id,))
            self.assertTrue(result and len(result) > 0)
            self.assertEqual(result[0]['RiskScore'], 75.5)
            self.assertEqual(result[0]['ChronicConditionFlag'], 1)
            self.assertEqual(result[0]['LifestyleRiskFactor'], 'Test')
            self.assertEqual(result[0]['ClaimFrequencyTier'], 'Test')
            self.assertEqual(result[0]['PredictedChurn'], 0.25)
            
            # Reset the values
            execute_non_query("""
                UPDATE Insurance.Members 
                SET RiskScore = NULL, 
                    ChronicConditionFlag = 0, 
                    LifestyleRiskFactor = NULL, 
                    ClaimFrequencyTier = NULL, 
                    PredictedChurn = NULL 
                WHERE MemberID = ?
            """, (member_id,))
        except Exception as e:
            self.fail(f"Error testing Member enhanced fields: {e}")

if __name__ == '__main__':
    unittest.main()