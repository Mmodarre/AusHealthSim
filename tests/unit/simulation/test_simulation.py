"""
Unit tests for the main simulation module.
"""
import pytest
from unittest.mock import patch, MagicMock, call
from datetime import date, datetime, timedelta

from health_insurance_au.simulation.simulation import HealthInsuranceSimulation
from health_insurance_au.models.models import (
    Member, CoveragePlan, Policy, Provider, Claim, PremiumPayment
)

class TestHealthInsuranceSimulation:
    """Tests for the HealthInsuranceSimulation class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.simulation = HealthInsuranceSimulation()
        
        # Create test data
        self.test_date = date(2022, 4, 15)
        
        # Test members
        self.test_members = [
            Member(
                first_name='John',
                last_name='Doe',
                date_of_birth=date(1980, 1, 1),
                gender='Male',
                address_line1='123 Main St',
                city='Sydney',
                state='NSW',
                post_code='2000',
                member_number='M10001'
            ),
            Member(
                first_name='Jane',
                last_name='Smith',
                date_of_birth=date(1985, 5, 15),
                gender='Female',
                address_line1='456 High St',
                city='Melbourne',
                state='VIC',
                post_code='3000',
                member_number='M10002'
            )
        ]
        
        # Test coverage plans
        self.test_plans = [
            CoveragePlan(
                plan_code='HOSP-GOLD',
                plan_name='Gold Hospital Cover',
                plan_type='Hospital',
                monthly_premium=200.0,
                annual_premium=2400.0,
                effective_date=date(2022, 1, 1),
                hospital_tier='Gold'
            ),
            CoveragePlan(
                plan_code='EXTRAS-COMP',
                plan_name='Comprehensive Extras Cover',
                plan_type='Extras',
                monthly_premium=100.0,
                annual_premium=1200.0,
                effective_date=date(2022, 1, 1)
            )
        ]
        
        # Test policies
        self.test_policies = [
            Policy(
                policy_number='POL10001',
                primary_member_id=1,
                plan_id=1,
                coverage_type='Single',
                start_date=date(2022, 1, 1),
                current_premium=200.0,
                last_premium_paid_date=date(2022, 3, 1),
                next_premium_due_date=date(2022, 4, 1)
            ),
            Policy(
                policy_number='POL10002',
                primary_member_id=2,
                plan_id=2,
                coverage_type='Family',
                start_date=date(2022, 2, 1),
                current_premium=150.0,
                last_premium_paid_date=date(2022, 3, 1),
                next_premium_due_date=date(2022, 4, 1)
            )
        ]
        # Add policy_id attribute to simulate database ID
        setattr(self.test_policies[0], 'policy_id', 1)
        setattr(self.test_policies[1], 'policy_id', 2)
        
        # Test providers
        self.test_providers = [
            Provider(
                provider_number='P10001',
                provider_name='Sydney Medical Center',
                provider_type='Hospital',
                address_line1='789 Health St',
                city='Sydney',
                state='NSW',
                post_code='2000'
            ),
            Provider(
                provider_number='P10002',
                provider_name='Melbourne Dental Clinic',
                provider_type='Dental',
                address_line1='101 Smile Ave',
                city='Melbourne',
                state='VIC',
                post_code='3000'
            )
        ]
    
    @patch('health_insurance_au.simulation.simulation.execute_query')
    def test_load_data_from_db(self, mock_execute_query):
        """Test loading data from the database."""
        # Arrange
        # Mock member data
        mock_execute_query.side_effect = [
            # Members
            [
                {
                    'MemberNumber': 'M10001',
                    'Title': 'Mr',
                    'FirstName': 'John',
                    'LastName': 'Doe',
                    'DateOfBirth': date(1980, 1, 1),
                    'Gender': 'Male',
                    'Email': 'john.doe@example.com',
                    'MobilePhone': '0412345678',
                    'HomePhone': None,
                    'AddressLine1': '123 Main St',
                    'AddressLine2': None,
                    'City': 'Sydney',
                    'State': 'NSW',
                    'PostCode': '2000',
                    'Country': 'Australia',
                    'MedicareNumber': '1234567890',
                    'LHCLoadingPercentage': 0.0,
                    'PHIRebateTier': 'Base',
                    'JoinDate': date(2022, 1, 1),
                    'IsActive': '1'
                }
            ],
            # Coverage plans
            [
                {
                    'PlanCode': 'HOSP-GOLD',
                    'PlanName': 'Gold Hospital Cover',
                    'PlanType': 'Hospital',
                    'HospitalTier': 'Gold',
                    'MonthlyPremium': 200.0,
                    'AnnualPremium': 2400.0,
                    'ExcessOptions': '[0, 250, 500]',
                    'WaitingPeriods': '{"general": 2, "pre-existing": 12}',
                    'CoverageDetails': '{"private_room": true, "ambulance": true}',
                    'IsActive': '1',
                    'EffectiveDate': date(2022, 1, 1),
                    'EndDate': None
                }
            ],
            # Policies
            [
                {
                    'PolicyID': 1,
                    'PolicyNumber': 'POL10001',
                    'PrimaryMemberID': 1,
                    'PlanID': 1,
                    'CoverageType': 'Single',
                    'StartDate': date(2022, 1, 1),
                    'EndDate': None,
                    'ExcessAmount': 0.0,
                    'PremiumFrequency': 'Monthly',
                    'CurrentPremium': 200.0,
                    'RebatePercentage': 0.0,
                    'LHCLoadingPercentage': 0.0,
                    'Status': 'Active',
                    'PaymentMethod': 'Direct Debit',
                    'LastPremiumPaidDate': date(2022, 3, 1),
                    'NextPremiumDueDate': date(2022, 4, 1)
                }
            ],
            # Providers
            [
                {
                    'ProviderNumber': 'P10001',
                    'ProviderName': 'Sydney Medical Center',
                    'ProviderType': 'Hospital',
                    'AddressLine1': '789 Health St',
                    'AddressLine2': None,
                    'City': 'Sydney',
                    'State': 'NSW',
                    'PostCode': '2000',
                    'Country': 'Australia',
                    'Phone': '0298765432',
                    'Email': 'info@sydneymedical.com',
                    'IsPreferredProvider': '1',
                    'AgreementStartDate': date(2022, 1, 1),
                    'AgreementEndDate': None,
                    'IsActive': '1'
                }
            ]
        ]
        
        # Act
        self.simulation.load_data_from_db()
        
        # Assert
        assert mock_execute_query.call_count == 4
        mock_execute_query.assert_has_calls([
            call("SELECT * FROM Insurance.Members"),
            call("SELECT * FROM Insurance.CoveragePlans"),
            call("SELECT * FROM Insurance.Policies"),
            call("SELECT * FROM Insurance.Providers")
        ])
        
        # Check that data was loaded correctly
        assert len(self.simulation.members) == 1
        assert self.simulation.members[0].member_number == 'M10001'
        assert self.simulation.members[0].first_name == 'John'
        
        assert len(self.simulation.coverage_plans) == 1
        assert self.simulation.coverage_plans[0].plan_code == 'HOSP-GOLD'
        
        assert len(self.simulation.policies) == 1
        assert self.simulation.policies[0].policy_number == 'POL10001'
        assert hasattr(self.simulation.policies[0], 'policy_id')
        assert self.simulation.policies[0].policy_id == 1
        
        assert len(self.simulation.providers) == 1
        assert self.simulation.providers[0].provider_number == 'P10001'
    
    @patch('health_insurance_au.simulation.simulation.load_sample_data')
    @patch('health_insurance_au.simulation.simulation.convert_to_members')
    @patch('health_insurance_au.simulation.simulation.bulk_insert')
    def test_add_members_from_static_data(self, mock_bulk_insert, mock_convert, mock_load_data):
        """Test adding new members from static data."""
        # Arrange
        mock_load_data.return_value = [{'first_name': 'John', 'last_name': 'Doe'}]
        mock_convert.return_value = self.test_members
        mock_bulk_insert.return_value = 2
        
        # Act
        self.simulation.add_members(count=2, simulation_date=self.test_date, use_dynamic_data=False)
        
        # Assert
        mock_load_data.assert_called_once()
        mock_convert.assert_called_once_with([{'first_name': 'John', 'last_name': 'Doe'}], 2)
        mock_bulk_insert.assert_called_once()
        
        # Check that members were added to the simulation
        assert len(self.simulation.members) == 2
    
    @patch('health_insurance_au.simulation.simulation.generate_dynamic_data')
    @patch('health_insurance_au.simulation.simulation.convert_dynamic_to_members')
    @patch('health_insurance_au.simulation.simulation.bulk_insert')
    def test_add_members_from_dynamic_data(self, mock_bulk_insert, mock_convert, mock_generate):
        """Test adding new members from dynamic data."""
        # Arrange
        mock_generate.return_value = [{'first_name': 'John', 'last_name': 'Doe'}]
        mock_convert.return_value = self.test_members
        mock_bulk_insert.return_value = 2
        
        # Act
        self.simulation.add_members(count=2, simulation_date=self.test_date, use_dynamic_data=True)
        
        # Assert
        mock_generate.assert_called_once_with(4)  # Should generate double the count
        mock_convert.assert_called_once_with([{'first_name': 'John', 'last_name': 'Doe'}], 2)
        mock_bulk_insert.assert_called_once()
        
        # Check that members were added to the simulation
        assert len(self.simulation.members) == 2
    
    @patch('health_insurance_au.simulation.simulation.generate_coverage_plans')
    @patch('health_insurance_au.simulation.simulation.bulk_insert')
    def test_add_coverage_plans(self, mock_bulk_insert, mock_generate_plans):
        """Test adding new coverage plans."""
        # Arrange
        mock_generate_plans.return_value = self.test_plans
        mock_bulk_insert.return_value = 2
        
        # Act
        self.simulation.add_coverage_plans(count=2, simulation_date=self.test_date)
        
        # Assert
        mock_generate_plans.assert_called_once_with(2, self.test_date)
        mock_bulk_insert.assert_called_once()
        
        # Check that plans were added to the simulation
        assert len(self.simulation.coverage_plans) == 2
    
    @patch('health_insurance_au.simulation.simulation.generate_providers')
    @patch('health_insurance_au.simulation.simulation.bulk_insert')
    def test_add_providers(self, mock_bulk_insert, mock_generate_providers):
        """Test adding new providers."""
        # Arrange
        mock_generate_providers.return_value = self.test_providers
        mock_bulk_insert.return_value = 2
        
        # Act
        self.simulation.add_providers(count=2, simulation_date=self.test_date)
        
        # Assert
        mock_generate_providers.assert_called_once_with(2, self.test_date)
        mock_bulk_insert.assert_called_once()
        
        # Check that providers were added to the simulation
        assert len(self.simulation.providers) == 2
    
    @patch('health_insurance_au.simulation.simulation.generate_policies')
    @patch('health_insurance_au.simulation.simulation.bulk_insert')
    def test_create_new_policies(self, mock_bulk_insert, mock_generate_policies):
        """Test creating new policies."""
        # Arrange
        self.simulation.members = self.test_members
        self.simulation.coverage_plans = self.test_plans
        
        mock_generate_policies.return_value = (self.test_policies, [])  # Policies and policy members
        mock_bulk_insert.return_value = 2
        
        # Act
        self.simulation.create_new_policies(count=2, simulation_date=self.test_date)
        
        # Assert
        mock_generate_policies.assert_called_once_with(
            self.test_members, self.test_plans, 2, self.test_date
        )
        assert mock_bulk_insert.call_count == 2  # Called for policies and policy members
        
        # Check that policies were added to the simulation
        assert len(self.simulation.policies) == 2
    
    @patch('health_insurance_au.simulation.simulation.random.sample')
    @patch('health_insurance_au.simulation.simulation.execute_non_query')
    def test_update_members(self, mock_execute_non_query, mock_random_sample):
        """Test updating members."""
        # Arrange
        self.simulation.members = self.test_members
        mock_random_sample.return_value = [self.test_members[0]]  # Select first member for update
        mock_execute_non_query.return_value = 1
        
        # Act
        self.simulation.update_members(percentage=50.0, simulation_date=self.test_date)
        
        # Assert
        mock_random_sample.assert_called_once_with(self.test_members, 1)
        mock_execute_non_query.assert_called_once()
        
        # Check that the query includes the member number
        args = mock_execute_non_query.call_args[0]
        assert 'M10001' in args[1]  # Member number should be in the parameters
    
    @patch('health_insurance_au.simulation.simulation.random.sample')
    @patch('health_insurance_au.simulation.simulation.execute_non_query')
    def test_process_policy_changes(self, mock_execute_non_query, mock_random_sample):
        """Test processing policy changes."""
        # Arrange
        self.simulation.policies = self.test_policies
        mock_random_sample.return_value = [self.test_policies[0]]  # Select first policy for update
        mock_execute_non_query.return_value = 1
        
        # Act
        self.simulation.process_policy_changes(percentage=50.0, simulation_date=self.test_date)
        
        # Assert
        mock_random_sample.assert_called_once_with(self.test_policies, 1)
        mock_execute_non_query.assert_called_once()
        
        # Check that the query includes the policy number
        args = mock_execute_non_query.call_args[0]
        assert 'POL10001' in args[1]  # Policy number should be in the parameters
    
    @patch('health_insurance_au.simulation.simulation.generate_hospital_claims')
    @patch('health_insurance_au.simulation.simulation.bulk_insert')
    def test_generate_hospital_claims(self, mock_bulk_insert, mock_generate_claims):
        """Test generating hospital claims."""
        # Arrange
        self.simulation.policies = self.test_policies
        self.simulation.members = self.test_members
        self.simulation.providers = self.test_providers
        
        test_claims = [
            Claim(
                claim_number='CLM10001',
                policy_id=1,
                member_id=1,
                provider_id=1,
                service_date=datetime(2022, 4, 10, 10, 0),
                submission_date=datetime(2022, 4, 12, 14, 30),
                claim_type='Hospital',
                service_description='Appendectomy',
                charged_amount=5000.0
            )
        ]
        
        mock_generate_claims.return_value = test_claims
        mock_bulk_insert.return_value = 1
        
        # Act
        self.simulation.generate_hospital_claims(count=1, simulation_date=self.test_date)
        
        # Assert
        mock_generate_claims.assert_called_once_with(
            self.test_policies, self.test_members, self.test_providers, 1, self.test_date
        )
        mock_bulk_insert.assert_called_once()
        
        # Check that claims were added to the simulation
        assert len(self.simulation.claims) == 1
    
    @patch('health_insurance_au.simulation.simulation.generate_general_treatment_claims')
    @patch('health_insurance_au.simulation.simulation.bulk_insert')
    def test_generate_general_treatment_claims(self, mock_bulk_insert, mock_generate_claims):
        """Test generating general treatment claims."""
        # Arrange
        self.simulation.policies = self.test_policies
        self.simulation.members = self.test_members
        self.simulation.providers = self.test_providers
        
        test_claims = [
            Claim(
                claim_number='CLM10002',
                policy_id=1,
                member_id=1,
                provider_id=2,
                service_date=datetime(2022, 4, 10, 9, 0),
                submission_date=datetime(2022, 4, 10, 10, 0),
                claim_type='General',
                service_description='Dental Checkup',
                charged_amount=150.0
            )
        ]
        
        mock_generate_claims.return_value = test_claims
        mock_bulk_insert.return_value = 1
        
        # Act
        self.simulation.generate_general_treatment_claims(count=1, simulation_date=self.test_date)
        
        # Assert
        mock_generate_claims.assert_called_once_with(
            self.test_policies, self.test_members, self.test_providers, 1, self.test_date
        )
        mock_bulk_insert.assert_called_once()
        
        # Check that claims were added to the simulation
        assert len(self.simulation.claims) == 1
    
    @patch('health_insurance_au.simulation.simulation.generate_premium_payments')
    @patch('health_insurance_au.simulation.simulation.bulk_insert')
    @patch('health_insurance_au.simulation.simulation.execute_non_query')
    def test_process_premium_payments(self, mock_execute_non_query, mock_bulk_insert, mock_generate_payments):
        """Test processing premium payments."""
        # Arrange
        self.simulation.policies = self.test_policies
        
        # Create test premium payments
        test_payments = [
            PremiumPayment(
                policy_id=1,
                payment_date=self.test_date,
                payment_amount=200.0,
                payment_method='Direct Debit',
                period_start_date=self.test_date,
                period_end_date=self.test_date + timedelta(days=30),
                payment_reference='PMT-20220415-12345'
            )
        ]
        
        # Update policy dates to simulate payment processing
        self.test_policies[0].last_premium_paid_date = self.test_date
        self.test_policies[0].next_premium_due_date = self.test_date + timedelta(days=30)
        
        mock_generate_payments.return_value = test_payments
        mock_bulk_insert.return_value = 1
        mock_execute_non_query.return_value = 1
        
        # Act
        self.simulation.process_premium_payments(simulation_date=self.test_date)
        
        # Assert
        mock_generate_payments.assert_called_once_with(self.test_policies, self.test_date)
        mock_bulk_insert.assert_called_once()
        mock_execute_non_query.assert_called_once()
        
        # Check that payments were added to the simulation
        assert len(self.simulation.premium_payments) == 1
    
    @patch('health_insurance_au.simulation.simulation.execute_query')
    @patch('health_insurance_au.simulation.simulation.random.sample')
    @patch('health_insurance_au.simulation.simulation.execute_non_query')
    def test_process_claim_assessments(self, mock_execute_non_query, mock_random_sample, mock_execute_query):
        """Test processing claim assessments."""
        # Arrange
        submitted_claims = [
            {
                'ClaimNumber': 'CLM10001',
                'Status': 'Submitted',
                'ServiceDate': self.test_date - timedelta(days=5),
                'SubmissionDate': self.test_date - timedelta(days=2)
            }
        ]
        
        mock_execute_query.return_value = submitted_claims
        mock_random_sample.return_value = submitted_claims
        mock_execute_non_query.return_value = 1
        
        # Act
        self.simulation.process_claim_assessments(percentage=100.0, simulation_date=self.test_date)
        
        # Assert
        mock_execute_query.assert_called_once()
        mock_random_sample.assert_called_once_with(submitted_claims, 1)
        mock_execute_non_query.assert_called_once()
        
        # Check that the query includes the claim number
        args = mock_execute_non_query.call_args[0]
        assert 'CLM10001' in args[1]  # Claim number should be in the parameters
    
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.load_data_from_db')
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.add_members')
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.add_coverage_plans')
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.add_providers')
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.create_new_policies')
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.update_members')
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.process_policy_changes')
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.generate_hospital_claims')
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.generate_general_treatment_claims')
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.process_premium_payments')
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.process_claim_assessments')
    def test_run_daily_simulation(
        self, mock_process_claims, mock_process_payments, mock_gen_general_claims, 
        mock_gen_hospital_claims, mock_process_policy_changes, mock_update_members,
        mock_create_policies, mock_add_providers, mock_add_plans, mock_add_members,
        mock_load_data
    ):
        """Test running a daily simulation."""
        # Act
        self.simulation.run_daily_simulation(
            simulation_date=self.test_date,
            new_members_count=5,
            add_new_plans=True,
            new_plans_count=2,
            new_providers_count=3,
            new_policies_count=4,
            hospital_claims_count=2,
            general_claims_count=5
        )
        
        # Assert
        mock_load_data.assert_called_once()
        mock_add_members.assert_called_once_with(5, self.test_date, True)
        mock_add_plans.assert_called_once_with(2, self.test_date)
        mock_add_providers.assert_called_once_with(3, self.test_date)
        mock_create_policies.assert_called_once_with(4, self.test_date)
        mock_update_members.assert_called_once()
        mock_process_policy_changes.assert_called_once()
        mock_gen_hospital_claims.assert_called_once_with(2, self.test_date)
        mock_gen_general_claims.assert_called_once_with(5, self.test_date)
        mock_process_payments.assert_called_once_with(self.test_date)
        mock_process_claims.assert_called_once()
    
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.run_daily_simulation')
    def test_run_historical_simulation_daily(self, mock_run_daily):
        """Test running a historical simulation with daily frequency."""
        # Arrange
        start_date = date(2022, 4, 1)
        end_date = date(2022, 4, 5)  # 5 days
        
        # Act
        self.simulation.run_historical_simulation(
            start_date=start_date,
            end_date=end_date,
            frequency='daily'
        )
        
        # Assert
        assert mock_run_daily.call_count == 5  # Called once for each day
        
        # Check that each day was simulated
        expected_dates = [date(2022, 4, 1), date(2022, 4, 2), date(2022, 4, 3), date(2022, 4, 4), date(2022, 4, 5)]
        for i, call_args in enumerate(mock_run_daily.call_args_list):
            assert call_args[1]['simulation_date'] == expected_dates[i]
    
    @patch('health_insurance_au.simulation.simulation.HealthInsuranceSimulation.run_daily_simulation')
    def test_run_historical_simulation_weekly(self, mock_run_daily):
        """Test running a historical simulation with weekly frequency."""
        # Arrange
        start_date = date(2022, 4, 1)
        end_date = date(2022, 4, 22)  # 3 weeks + 1 day
        
        # Act
        self.simulation.run_historical_simulation(
            start_date=start_date,
            end_date=end_date,
            frequency='weekly'
        )
        
        # Assert
        assert mock_run_daily.call_count == 4  # Called once for each week (and partial week)
        
        # Check that each week was simulated
        expected_dates = [date(2022, 4, 1), date(2022, 4, 8), date(2022, 4, 15), date(2022, 4, 22)]
        for i, call_args in enumerate(mock_run_daily.call_args_list):
            assert call_args[1]['simulation_date'] == expected_dates[i]