"""
Unit tests for enhanced simulation features.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import date

from health_insurance_au.data_generation.enhanced_simulation import run_enhanced_simulation
from health_insurance_au.data_generation.simulation_orchestrator import SimulationOrchestrator
from health_insurance_au.data_generation.fraud_patterns import FraudPatternGenerator
from health_insurance_au.data_generation.financial_transactions import FinancialTransactionGenerator
from health_insurance_au.data_generation.provider_billing import ProviderBillingGenerator
from health_insurance_au.data_generation.claim_patterns import ClaimPatternGenerator
from health_insurance_au.data_generation.actuarial_data import ActuarialDataGenerator

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

if __name__ == '__main__':
    unittest.main()