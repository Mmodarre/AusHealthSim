"""
Unit tests for the main simulation module.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timedelta

# Import the conftest module to ensure the pyodbc mock is set up
from tests.conftest import *

from health_insurance_au.simulation.simulation import HealthInsuranceSimulation


def test_run_daily_simulation():
    """Test running a daily simulation."""
    # Create a simulation instance
    simulation = HealthInsuranceSimulation()
    
    # Set up mocks for all the simulation components
    with patch.object(simulation, 'load_data_from_db') as mock_load_data, \
         patch.object(simulation, 'add_members') as mock_add_members, \
         patch.object(simulation, 'add_coverage_plans') as mock_add_plans, \
         patch.object(simulation, 'create_new_policies') as mock_create_policies, \
         patch.object(simulation, 'update_members') as mock_update_members, \
         patch.object(simulation, 'process_policy_changes') as mock_process_policy_changes, \
         patch.object(simulation, 'generate_hospital_claims') as mock_generate_hospital_claims, \
         patch.object(simulation, 'generate_general_treatment_claims') as mock_generate_general_claims, \
         patch.object(simulation, 'process_premium_payments') as mock_process_premium_payments, \
         patch.object(simulation, 'process_claim_assessments') as mock_process_claim_assessments:
        
        # Run the daily simulation with default parameters
        simulation.run_daily_simulation(
            simulation_date=date(2023, 5, 15),
            new_members_count=5,
            add_new_plans=True,
            new_plans_count=1,
            new_policies_count=3,
            hospital_claims_count=10,
            general_claims_count=20
        )
        
        # Verify all simulation components were called
        mock_load_data.assert_called_once()
        mock_add_members.assert_called_once_with(5)
        mock_add_plans.assert_called_once_with(1)
        mock_create_policies.assert_called_once_with(3)
        mock_update_members.assert_called_once()
        mock_process_policy_changes.assert_called_once()
        mock_generate_hospital_claims.assert_called_once_with(10)
        mock_generate_general_claims.assert_called_once_with(20)
        mock_process_premium_payments.assert_called_once_with(date(2023, 5, 15))
        mock_process_claim_assessments.assert_called_once()


def test_run_daily_simulation_with_skips():
    """Test running a daily simulation with some components skipped."""
    # Create a simulation instance
    simulation = HealthInsuranceSimulation()
    
    # Set up mocks for all the simulation components
    with patch.object(simulation, 'load_data_from_db') as mock_load_data, \
         patch.object(simulation, 'add_members') as mock_add_members, \
         patch.object(simulation, 'add_coverage_plans') as mock_add_plans, \
         patch.object(simulation, 'create_new_policies') as mock_create_policies, \
         patch.object(simulation, 'update_members') as mock_update_members, \
         patch.object(simulation, 'process_policy_changes') as mock_process_policy_changes, \
         patch.object(simulation, 'generate_hospital_claims') as mock_generate_hospital_claims, \
         patch.object(simulation, 'generate_general_treatment_claims') as mock_generate_general_claims, \
         patch.object(simulation, 'process_premium_payments') as mock_process_premium_payments, \
         patch.object(simulation, 'process_claim_assessments') as mock_process_claim_assessments:
        
        # Run the daily simulation with some components skipped
        simulation.run_daily_simulation(
            simulation_date=date(2023, 5, 15),
            add_new_members=False,  # Skip members
            new_members_count=0,
            add_new_plans=False,    # Skip plans
            new_plans_count=0,
            new_policies_count=3,
            hospital_claims_count=10,
            general_claims_count=20,
            process_premium_payments=False  # Skip payments
        )
        
        # Verify skipped components were not called
        mock_add_members.assert_not_called()
        mock_add_plans.assert_not_called()
        mock_process_premium_payments.assert_not_called()
        
        # Verify non-skipped components were called
        mock_load_data.assert_called_once()
        mock_create_policies.assert_called_once_with(3)
        mock_update_members.assert_called_once()
        mock_process_policy_changes.assert_called_once()
        mock_generate_hospital_claims.assert_called_once_with(10)
        mock_generate_general_claims.assert_called_once_with(20)
        mock_process_claim_assessments.assert_called_once()


def test_run_historical_simulation():
    """Test running a historical simulation."""
    # Create a simulation instance
    simulation = HealthInsuranceSimulation()
    
    # Set up mocks for the simulation components
    with patch.object(simulation, 'add_members') as mock_add_members, \
         patch.object(simulation, 'add_providers') as mock_add_providers, \
         patch.object(simulation, 'add_coverage_plans') as mock_add_plans, \
         patch.object(simulation, 'create_new_policies') as mock_create_policies, \
         patch.object(simulation, 'run_daily_simulation') as mock_run_daily_simulation:
        
        # Run a historical simulation for one week with daily frequency
        start_date = date(2023, 5, 1)
        end_date = date(2023, 5, 7)
        
        simulation.run_historical_simulation(
            start_date=start_date,
            end_date=end_date,
            frequency='daily'
        )
        
        # Verify initial data was set up
        mock_add_members.assert_called_once_with(100)
        mock_add_providers.assert_called_once_with(50)
        mock_add_plans.assert_called_once_with(15)
        mock_create_policies.assert_called_once_with(50)
        
        # Verify daily simulation was called for each day
        assert mock_run_daily_simulation.call_count == 7
        
        # Verify the simulation dates
        for i in range(7):
            expected_date = start_date + timedelta(days=i)
            # Check that one of the calls used this date
            found = False
            for call in mock_run_daily_simulation.call_args_list:
                if call[1].get('simulation_date') == expected_date:
                    found = True
                    break
            assert found, f"No simulation run found for date {expected_date}"


def test_run_historical_simulation_weekly():
    """Test running a historical simulation with weekly frequency."""
    # Create a simulation instance
    simulation = HealthInsuranceSimulation()
    
    # Set up mocks for the simulation components
    with patch.object(simulation, 'add_members') as mock_add_members, \
         patch.object(simulation, 'add_providers') as mock_add_providers, \
         patch.object(simulation, 'add_coverage_plans') as mock_add_plans, \
         patch.object(simulation, 'create_new_policies') as mock_create_policies, \
         patch.object(simulation, 'run_daily_simulation') as mock_run_daily_simulation:
        
        # Run a historical simulation for one month with weekly frequency
        start_date = date(2023, 5, 1)
        end_date = date(2023, 5, 29)  # 4 weeks + 1 day
        
        simulation.run_historical_simulation(
            start_date=start_date,
            end_date=end_date,
            frequency='weekly'
        )
        
        # Verify initial data was set up
        mock_add_members.assert_called_once()
        mock_add_providers.assert_called_once()
        mock_add_plans.assert_called_once()
        mock_create_policies.assert_called_once()
        
        # Verify daily simulation was called for each week (5 times)
        assert mock_run_daily_simulation.call_count == 5
        
        # Verify the simulation dates
        for i in range(5):
            expected_date = start_date + timedelta(days=i*7)
            # Check that one of the calls used this date
            found = False
            for call in mock_run_daily_simulation.call_args_list:
                if call[1].get('simulation_date') == expected_date:
                    found = True
                    break
            assert found, f"No simulation run found for date {expected_date}"


def test_run_historical_simulation_monthly():
    """Test running a historical simulation with monthly frequency."""
    # Create a simulation instance
    simulation = HealthInsuranceSimulation()
    
    # Set up mocks for the simulation components
    with patch.object(simulation, 'add_members') as mock_add_members, \
         patch.object(simulation, 'add_providers') as mock_add_providers, \
         patch.object(simulation, 'add_coverage_plans') as mock_add_plans, \
         patch.object(simulation, 'create_new_policies') as mock_create_policies, \
         patch.object(simulation, 'run_daily_simulation') as mock_run_daily_simulation:
        
        # Run a historical simulation for 3 months with monthly frequency
        start_date = date(2023, 1, 1)
        end_date = date(2023, 3, 31)
        
        simulation.run_historical_simulation(
            start_date=start_date,
            end_date=end_date,
            frequency='monthly'
        )
        
        # Verify initial data was set up
        mock_add_members.assert_called_once()
        mock_add_providers.assert_called_once()
        mock_add_plans.assert_called_once()
        mock_create_policies.assert_called_once()
        
        # Verify daily simulation was called for each month (3 times)
        assert mock_run_daily_simulation.call_count == 3
        
        # Check the dates (this is approximate since months vary in length)
        expected_dates = [
            date(2023, 1, 1),
            date(2023, 2, 1),
            date(2023, 3, 1)
        ]
        
        for i in range(3):
            expected_date = expected_dates[i]
            # Check that one of the calls used a date close to the expected date
            found = False
            for call in mock_run_daily_simulation.call_args_list:
                call_date = call[1].get('simulation_date')
                if abs((call_date - expected_date).days) <= 2:  # Allow 2 days difference
                    found = True
                    break
            assert found, f"No simulation run found for date near {expected_date}"


def test_invalid_frequency():
    """Test handling of invalid frequency in historical simulation."""
    # Create a simulation instance
    simulation = HealthInsuranceSimulation()
    
    # Set up mocks for the simulation components
    with patch.object(simulation, 'add_members') as mock_add_members, \
         patch.object(simulation, 'add_providers') as mock_add_providers, \
         patch.object(simulation, 'add_coverage_plans') as mock_add_plans, \
         patch.object(simulation, 'create_new_policies') as mock_create_policies, \
         patch.object(simulation, 'run_daily_simulation') as mock_run_daily_simulation:
        
        # Run a historical simulation with invalid frequency
        start_date = date(2023, 5, 1)
        end_date = date(2023, 5, 7)
        
        simulation.run_historical_simulation(
            start_date=start_date,
            end_date=end_date,
            frequency='invalid'
        )
        
        # Verify initial data was set up
        mock_add_members.assert_called_once()
        mock_add_providers.assert_called_once()
        mock_add_plans.assert_called_once()
        mock_create_policies.assert_called_once()
        
        # Verify daily simulation was not called due to invalid frequency
        mock_run_daily_simulation.assert_not_called()