"""
Unit tests for enhanced simulation features.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY
from datetime import date, datetime

from health_insurance_au.data_generation.enhanced_simulation import run_enhanced_simulation
from health_insurance_au.data_generation.simulation_orchestrator import SimulationOrchestrator
from health_insurance_au.data_generation.fraud_patterns import FraudPatternGenerator
from health_insurance_au.data_generation.financial_transactions import FinancialTransactionGenerator
from health_insurance_au.data_generation.provider_billing import ProviderBillingGenerator
from health_insurance_au.data_generation.claim_patterns import ClaimPatternGenerator
from health_insurance_au.data_generation.actuarial_data import ActuarialDataGenerator
from health_insurance_au.models.models import (
    Member, Policy, Claim, Provider, 
    FraudIndicator, FinancialTransaction, ActuarialMetric, ClaimPattern
)

class TestEnhancedSimulation(unittest.TestCase):
    """Test cases for enhanced simulation features."""
    
    @patch('health_insurance_au.data_generation.enhanced_simulation.SimulationOrchestrator')
    def test_run_enhanced_simulation(self, mock_orchestrator_class):
        """Test that run_enhanced_simulation calls the orchestrator correctly."""
        # Setup mock
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.run_enhanced_simulation.return_value = {
            'simulation_date': date(2023, 1, 1),
            'members_updated': 10,
            'policies_updated': 5,
            'providers_updated': 3,
            'claims_updated': 20,
            'claim_patterns_generated': 5,
            'financial_transactions_generated': 15,
            'actuarial_metrics_generated': 30
        }
        
        # Call function
        simulation_date = date(2023, 1, 1)
        config = {
            'generate_member_risk_profiles': True,
            'generate_policy_risk_attributes': True,
            'generate_provider_billing_attributes': True,
            'apply_fraud_patterns': True,
            'generate_claim_patterns': True,
            'generate_financial_transactions': True,
            'generate_actuarial_metrics': True
        }
        
        result = run_enhanced_simulation(simulation_date, config)
        
        # Assertions
        mock_orchestrator_class.assert_called_once()
        mock_orchestrator.run_enhanced_simulation.assert_called_once_with(simulation_date, config)
        self.assertEqual(result['members_updated'], 10)
        self.assertEqual(result['policies_updated'], 5)
        self.assertEqual(result['providers_updated'], 3)
        self.assertEqual(result['claims_updated'], 20)
        self.assertEqual(result['claim_patterns_generated'], 5)
        self.assertEqual(result['financial_transactions_generated'], 15)
        self.assertEqual(result['actuarial_metrics_generated'], 30)
    
    @patch('health_insurance_au.data_generation.simulation_orchestrator.FraudPatternGenerator')
    @patch('health_insurance_au.data_generation.simulation_orchestrator.FinancialTransactionGenerator')
    @patch('health_insurance_au.data_generation.simulation_orchestrator.ProviderBillingGenerator')
    @patch('health_insurance_au.data_generation.simulation_orchestrator.ClaimPatternGenerator')
    @patch('health_insurance_au.data_generation.simulation_orchestrator.ActuarialDataGenerator')
    def test_simulation_orchestrator_initialization(self, mock_actuarial, mock_claim_pattern, 
                                                 mock_provider_billing, mock_financial, mock_fraud):
        """Test that SimulationOrchestrator initializes all generators."""
        # Setup mocks
        mock_fraud_instance = MagicMock()
        mock_financial_instance = MagicMock()
        mock_provider_billing_instance = MagicMock()
        mock_claim_pattern_instance = MagicMock()
        mock_actuarial_instance = MagicMock()
        
        mock_fraud.return_value = mock_fraud_instance
        mock_financial.return_value = mock_financial_instance
        mock_provider_billing.return_value = mock_provider_billing_instance
        mock_claim_pattern.return_value = mock_claim_pattern_instance
        mock_actuarial.return_value = mock_actuarial_instance
        
        # Create orchestrator
        orchestrator = SimulationOrchestrator()
        
        # Assertions
        mock_fraud.assert_called_once()
        mock_financial.assert_called_once()
        mock_provider_billing.assert_called_once()
        mock_claim_pattern.assert_called_once()
        mock_actuarial.assert_called_once()
        
        self.assertEqual(orchestrator.fraud_generator, mock_fraud_instance)
        self.assertEqual(orchestrator.financial_generator, mock_financial_instance)
        self.assertEqual(orchestrator.provider_billing_generator, mock_provider_billing_instance)
        self.assertEqual(orchestrator.claim_pattern_generator, mock_claim_pattern_instance)
        self.assertEqual(orchestrator.actuarial_generator, mock_actuarial_instance)
    
    @patch('health_insurance_au.data_generation.fraud_patterns.execute_query')
    def test_fraud_pattern_generator_load_indicators(self, mock_execute_query):
        """Test that FraudPatternGenerator loads fraud indicators from the database."""
        # Setup mock
        mock_execute_query.return_value = [
            {
                'IndicatorID': 1,
                'IndicatorCode': 'DUP_CLAIM',
                'IndicatorName': 'Duplicate Claim',
                'IndicatorDescription': 'Multiple claims for the same service on the same date',
                'SeverityLevel': 'High',
                'DetectionLogic': 'Claims with identical service dates, service descriptions, and member IDs within a 30-day period',
                'CreatedDate': date(2023, 1, 1),
                'LastModified': date(2023, 1, 1)
            }
        ]
        
        # Create generator
        generator = FraudPatternGenerator()
        
        # Assertions
        mock_execute_query.assert_called_once_with("SELECT * FROM Insurance.FraudIndicators")
        self.assertEqual(len(generator.fraud_indicators), 1)
        self.assertEqual(generator.fraud_indicators[0].indicator_code, 'DUP_CLAIM')
        self.assertEqual(generator.fraud_indicators[0].indicator_name, 'Duplicate Claim')
        self.assertEqual(generator.fraud_indicators[0].severity_level, 'High')
    
    @patch('health_insurance_au.data_generation.fraud_patterns.execute_query')
    @patch('health_insurance_au.data_generation.fraud_patterns.execute_non_query')
    def test_fraud_pattern_generator_apply_patterns(self, mock_execute_non_query, mock_execute_query):
        """Test that FraudPatternGenerator applies fraud patterns to claims."""
        # Setup mocks
        mock_execute_query.side_effect = [
            # First call - fraud indicators
            [
                {
                    'IndicatorID': 1,
                    'IndicatorCode': 'DUP_CLAIM',
                    'IndicatorName': 'Duplicate Claim',
                    'IndicatorDescription': 'Multiple claims for the same service on the same date',
                    'SeverityLevel': 'High',
                    'DetectionLogic': 'Claims with identical service dates, service descriptions, and member IDs within a 30-day period',
                    'CreatedDate': date(2023, 1, 1),
                    'LastModified': date(2023, 1, 1)
                }
            ],
            # Second call - claims
            [
                {
                    'ClaimID': 1,
                    'ClaimNumber': 'C123456',
                    'PolicyID': 1,
                    'MemberID': 1,
                    'ProviderID': 1,
                    'ServiceDate': date(2023, 1, 1),
                    'SubmissionDate': date(2023, 1, 5),
                    'ClaimType': 'Hospital',
                    'ServiceDescription': 'Appendectomy',
                    'ChargedAmount': 1000.0,
                    'MedicareAmount': 500.0,
                    'InsuranceAmount': 400.0,
                    'GapAmount': 100.0,
                    'Status': 'Submitted',
                    'LastModified': datetime(2023, 1, 5)
                }
            ]
        ]
        
        # Create generator and apply patterns
        generator = FraudPatternGenerator()
        simulation_date = date(2023, 1, 10)
        result = generator.apply_fraud_patterns(simulation_date, fraud_rate=0.5)
        
        # Assertions
        self.assertEqual(mock_execute_query.call_count, 2)
        mock_execute_non_query.assert_called()
        self.assertEqual(result['claims_updated'], 1)
    
    @patch('health_insurance_au.data_generation.financial_transactions.execute_query')
    @patch('health_insurance_au.data_generation.financial_transactions.execute_non_query')
    @patch('health_insurance_au.data_generation.financial_transactions.bulk_insert')
    def test_financial_transaction_generator(self, mock_bulk_insert, mock_execute_non_query, mock_execute_query):
        """Test that FinancialTransactionGenerator generates transactions."""
        # Setup mocks
        mock_execute_query.side_effect = [
            # First call - policies
            [
                {
                    'PolicyID': 1,
                    'PolicyNumber': 'P123456',
                    'PrimaryMemberID': 1,
                    'PlanID': 1,
                    'CoverageType': 'Hospital',
                    'StartDate': date(2023, 1, 1),
                    'CurrentPremium': 200.0,
                    'Status': 'Active',
                    'LastModified': datetime(2023, 1, 1)
                }
            ],
            # Second call - claims
            [
                {
                    'ClaimID': 1,
                    'ClaimNumber': 'C123456',
                    'PolicyID': 1,
                    'MemberID': 1,
                    'ProviderID': 1,
                    'ServiceDate': date(2023, 1, 1),
                    'SubmissionDate': date(2023, 1, 5),
                    'ClaimType': 'Hospital',
                    'ServiceDescription': 'Appendectomy',
                    'ChargedAmount': 1000.0,
                    'MedicareAmount': 500.0,
                    'InsuranceAmount': 400.0,
                    'GapAmount': 100.0,
                    'Status': 'Approved',
                    'LastModified': datetime(2023, 1, 5)
                }
            ],
            # Third call - policies for refunds
            [],
            # Fourth call - policies for adjustments
            []
        ]
        
        mock_bulk_insert.return_value = 2  # 2 rows inserted
        
        # Create generator and generate transactions
        generator = FinancialTransactionGenerator()
        simulation_date = date(2023, 1, 10)
        result = generator.generate_transactions(simulation_date)
        
        # Assertions
        self.assertEqual(mock_execute_query.call_count, 4)
        mock_bulk_insert.assert_called_once()
        self.assertEqual(result['transactions_generated'], 2)
    
    @patch('health_insurance_au.data_generation.provider_billing.execute_query')
    @patch('health_insurance_au.data_generation.provider_billing.execute_non_query')
    def test_provider_billing_generator(self, mock_execute_non_query, mock_execute_query):
        """Test that ProviderBillingGenerator generates billing attributes."""
        # Setup mocks
        mock_execute_query.return_value = [
            {
                'ProviderID': 1,
                'ProviderNumber': 'PR123456',
                'ProviderName': 'Sydney Medical Center',
                'ProviderType': 'Hospital',
                'AddressLine1': '456 Health St',
                'City': 'Sydney',
                'State': 'NSW',
                'PostCode': '2000',
                'Country': 'Australia',
                'LastModified': datetime(2023, 1, 1)
            }
        ]
        
        mock_execute_non_query.return_value = 1  # 1 row updated
        
        # Create generator and generate billing attributes
        generator = ProviderBillingGenerator()
        simulation_date = date(2023, 1, 10)
        result = generator.generate_billing_attributes(simulation_date)
        
        # Assertions
        mock_execute_query.assert_called_once()
        mock_execute_non_query.assert_called()
        self.assertEqual(result['providers_updated'], 1)
    
    @patch('health_insurance_au.data_generation.claim_patterns.execute_query')
    def test_claim_pattern_generator(self, mock_execute_query):
        """Test that ClaimPatternGenerator generates claim patterns."""
        # Setup mocks
        mock_execute_query.side_effect = [
            # First call - members
            [
                {
                    'MemberID': 1,
                    'MemberNumber': 'M123456',
                    'FirstName': 'John',
                    'LastName': 'Smith',
                    'DateOfBirth': date(1980, 1, 1),
                    'Gender': 'M',
                    'LastModified': datetime(2023, 1, 1)
                }
            ],
            # Second call - providers
            [
                {
                    'ProviderID': 1,
                    'ProviderNumber': 'PR123456',
                    'ProviderName': 'Sydney Medical Center',
                    'ProviderType': 'Hospital',
                    'LastModified': datetime(2023, 1, 1)
                }
            ],
            # Third call - claims
            []  # No claims, so no patterns will be generated
        ]
        
        # Create generator and generate patterns
        generator = ClaimPatternGenerator()
        simulation_date = date(2023, 1, 20)
        result = generator.generate_patterns(simulation_date)
        
        # Assertions
        self.assertEqual(mock_execute_query.call_count, 3)
        self.assertEqual(result['patterns_generated'], 0)  # No patterns should be generated
    
    @patch('health_insurance_au.data_generation.actuarial_data.execute_query')
    @patch('health_insurance_au.data_generation.actuarial_data.bulk_insert')
    def test_actuarial_data_generator(self, mock_bulk_insert, mock_execute_query):
        """Test that ActuarialDataGenerator generates actuarial metrics."""
        # Setup mocks
        mock_execute_query.return_value = [
            {
                'AgeGroup': '18-30',
                'Gender': 'M',
                'StateTerritory': 'NSW',
                'ProductCategory': 'Gold',
                'TotalPremiums': 10000.0,
                'TotalClaims': 8000.0,
                'MemberCount': 100
            }
        ]
        
        mock_bulk_insert.return_value = 3  # 3 metrics inserted
        
        # Create generator and generate metrics
        generator = ActuarialDataGenerator()
        simulation_date = date(2023, 1, 31)  # End of month
        result = generator.generate_metrics(simulation_date)
        
        # Assertions
        mock_execute_query.assert_called_once()
        mock_bulk_insert.assert_called_once()
        self.assertEqual(result['metrics_generated'], 3)
    
    @patch('health_insurance_au.data_generation.simulation_orchestrator.FraudPatternGenerator')
    @patch('health_insurance_au.data_generation.simulation_orchestrator.FinancialTransactionGenerator')
    @patch('health_insurance_au.data_generation.simulation_orchestrator.ProviderBillingGenerator')
    @patch('health_insurance_au.data_generation.simulation_orchestrator.ClaimPatternGenerator')
    @patch('health_insurance_au.data_generation.simulation_orchestrator.ActuarialDataGenerator')
    def test_simulation_orchestrator_run_enhanced_simulation(self, mock_actuarial, mock_claim_pattern, 
                                                           mock_provider_billing, mock_financial, mock_fraud):
        """Test that SimulationOrchestrator runs enhanced simulation correctly."""
        # Setup mocks
        mock_fraud_instance = MagicMock()
        mock_financial_instance = MagicMock()
        mock_provider_billing_instance = MagicMock()
        mock_claim_pattern_instance = MagicMock()
        mock_actuarial_instance = MagicMock()
        
        mock_fraud.return_value = mock_fraud_instance
        mock_financial.return_value = mock_financial_instance
        mock_provider_billing.return_value = mock_provider_billing_instance
        mock_claim_pattern.return_value = mock_claim_pattern_instance
        mock_actuarial.return_value = mock_actuarial_instance
        
        # Set up return values for each generator
        mock_fraud_instance.apply_fraud_patterns.return_value = {'claims_updated': 10}
        mock_financial_instance.generate_transactions.return_value = {'transactions_generated': 20}
        mock_provider_billing_instance.generate_billing_attributes.return_value = {'providers_updated': 5}
        mock_claim_pattern_instance.generate_patterns.return_value = {'patterns_generated': 15}
        mock_actuarial_instance.generate_metrics.return_value = {'metrics_generated': 30}
        
        # Create orchestrator and run simulation
        orchestrator = SimulationOrchestrator()
        simulation_date = date(2023, 1, 31)
        config = {
            'generate_member_risk_profiles': True,
            'generate_policy_risk_attributes': True,
            'generate_provider_billing_attributes': True,
            'apply_fraud_patterns': True,
            'generate_claim_patterns': True,
            'generate_financial_transactions': True,
            'generate_actuarial_metrics': True
        }
        
        result = orchestrator.run_enhanced_simulation(simulation_date, config)
        
        # Assertions
        mock_fraud_instance.apply_fraud_patterns.assert_called_once()
        mock_financial_instance.generate_transactions.assert_called_once()
        mock_provider_billing_instance.generate_billing_attributes.assert_called_once()
        mock_claim_pattern_instance.generate_patterns.assert_called_once()
        mock_actuarial_instance.generate_metrics.assert_called_once()
        
        self.assertEqual(result['claims_updated'], 10)
        self.assertEqual(result['financial_transactions_generated'], 20)
        self.assertEqual(result['providers_updated'], 5)
        self.assertEqual(result['claim_patterns_generated'], 15)
        self.assertEqual(result['actuarial_metrics_generated'], 30)
    
    @patch('health_insurance_au.data_generation.simulation_orchestrator.FraudPatternGenerator')
    @patch('health_insurance_au.data_generation.simulation_orchestrator.FinancialTransactionGenerator')
    @patch('health_insurance_au.data_generation.simulation_orchestrator.ProviderBillingGenerator')
    @patch('health_insurance_au.data_generation.simulation_orchestrator.ClaimPatternGenerator')
    @patch('health_insurance_au.data_generation.simulation_orchestrator.ActuarialDataGenerator')
    def test_simulation_orchestrator_selective_features(self, mock_actuarial, mock_claim_pattern, 
                                                      mock_provider_billing, mock_financial, mock_fraud):
        """Test that SimulationOrchestrator only runs enabled features."""
        # Setup mocks
        mock_fraud_instance = MagicMock()
        mock_financial_instance = MagicMock()
        mock_provider_billing_instance = MagicMock()
        mock_claim_pattern_instance = MagicMock()
        mock_actuarial_instance = MagicMock()
        
        mock_fraud.return_value = mock_fraud_instance
        mock_financial.return_value = mock_financial_instance
        mock_provider_billing.return_value = mock_provider_billing_instance
        mock_claim_pattern.return_value = mock_claim_pattern_instance
        mock_actuarial.return_value = mock_actuarial_instance
        
        # Create orchestrator and run simulation with only some features enabled
        orchestrator = SimulationOrchestrator()
        simulation_date = date(2023, 1, 31)
        config = {
            'generate_member_risk_profiles': False,
            'generate_policy_risk_attributes': False,
            'generate_provider_billing_attributes': True,
            'apply_fraud_patterns': True,
            'generate_claim_patterns': False,
            'generate_financial_transactions': True,
            'generate_actuarial_metrics': False
        }
        
        orchestrator.run_enhanced_simulation(simulation_date, config)
        
        # Assertions - these should be called
        mock_fraud_instance.apply_fraud_patterns.assert_called_once()
        mock_financial_instance.generate_transactions.assert_called_once()
        mock_provider_billing_instance.generate_billing_attributes.assert_called_once()
        
        # Assertions - these should not be called
        mock_claim_pattern_instance.generate_patterns.assert_not_called()
        mock_actuarial_instance.generate_metrics.assert_not_called()

if __name__ == '__main__':
    unittest.main()