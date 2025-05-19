"""
Integration tests for simulation components.
"""
import pytest
from datetime import date, timedelta
import os
import sys
import uuid

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from health_insurance_au.utils.db_utils import execute_query, execute_non_query
from health_insurance_au.simulation.simulation import HealthInsuranceSimulation
from health_insurance_au.simulation.claims import generate_hospital_claims, generate_general_treatment_claims
from health_insurance_au.simulation.payments import generate_premium_payments
from health_insurance_au.models.models import Policy


class TestSimulationIntegration:
    """Integration tests for simulation components."""
    
    @pytest.fixture
    def simulation(self, simulation_date):
        """Create a simulation instance."""
        return HealthInsuranceSimulation()
    
    def test_add_members(self, simulation, simulation_date):
        """Test adding new members."""
        # Get initial count of members
        initial_count = execute_query("SELECT COUNT(*) AS count FROM Insurance.Members")[0]['count']
        
        # Add new members
        new_members_count = 3
        simulation.add_members(new_members_count, simulation_date)
        
        # Get new count of members
        new_count = execute_query("SELECT COUNT(*) AS count FROM Insurance.Members")[0]['count']
        
        # Check that new members were added
        assert new_count > initial_count
        
        # Check that the new members have the correct LastModified date
        new_members = execute_query(f"""
        SELECT *
        FROM Insurance.Members
        WHERE CONVERT(date, LastModified) = '{simulation_date.strftime('%Y-%m-%d')}'
        """)
        
        assert len(new_members) > 0
    
    def test_add_coverage_plans(self, simulation, simulation_date):
        """Test adding new coverage plans."""
        # Get initial count of plans
        initial_count = execute_query("SELECT COUNT(*) AS count FROM Insurance.CoveragePlans")[0]['count']
        
        # Add new plans
        new_plans_count = 2
        simulation.add_coverage_plans(new_plans_count, simulation_date)
        
        # Get new count of plans
        new_count = execute_query("SELECT COUNT(*) AS count FROM Insurance.CoveragePlans")[0]['count']
        
        # Check that new plans were added
        assert new_count > initial_count
        
        # Check that the new plans have the correct LastModified date
        new_plans = execute_query(f"""
        SELECT *
        FROM Insurance.CoveragePlans
        WHERE CONVERT(date, LastModified) = '{simulation_date.strftime('%Y-%m-%d')}'
        """)
        
        assert len(new_plans) > 0
    
    def test_create_new_policies(self, simulation, simulation_date):
        """Test creating new policies."""
        # First, make sure we have members and plans
        simulation.add_members(5, simulation_date)
        simulation.add_coverage_plans(2, simulation_date)
        
        # Load data from database
        simulation.load_data_from_db()
        
        # Get initial count of policies
        initial_count = execute_query("SELECT COUNT(*) AS count FROM Insurance.Policies")[0]['count']
        
        # Create new policies
        new_policies_count = 2
        simulation.create_new_policies(new_policies_count, simulation_date)
        
        # Get new count of policies
        new_count = execute_query("SELECT COUNT(*) AS count FROM Insurance.Policies")[0]['count']
        
        # Check that new policies were added
        assert new_count > initial_count
        
        # Check that the new policies have the correct LastModified date
        new_policies = execute_query(f"""
        SELECT *
        FROM Insurance.Policies
        WHERE CONVERT(date, LastModified) = '{simulation_date.strftime('%Y-%m-%d')}'
        """)
        
        assert len(new_policies) > 0
    
    def test_process_premium_payments(self, simulation_date):
        """Test processing premium payments."""
        # Get initial count of premium payments
        initial_count = execute_query("SELECT COUNT(*) AS count FROM Insurance.PremiumPayments")[0]['count']
        
        # Get active policies
        policies_data = execute_query("""
        SELECT p.*, cp.MonthlyPremium as current_premium
        FROM Insurance.Policies p
        JOIN Insurance.CoveragePlans cp ON p.PlanID = cp.PlanID
        WHERE p.Status = 'Active'
        AND p.NextPremiumDueDate <= ?
        """, (simulation_date,))
        
        # Convert to Policy objects
        policies = []
        for p in policies_data:
            policy = Policy(
                policy_number=p['PolicyNumber'],
                primary_member_id=p['PrimaryMemberID'],
                plan_id=p['PlanID'],
                coverage_type=p['CoverageType'],
                start_date=p['StartDate'],
                current_premium=float(p['current_premium']),
                premium_frequency=p['PremiumFrequency'],
                excess_amount=float(p['ExcessAmount']),
                rebate_percentage=float(p['RebatePercentage']),
                lhc_loading_percentage=float(p['LHCLoadingPercentage']),
                status=p['Status'],
                payment_method=p['PaymentMethod'],
                end_date=p['EndDate'],
                last_premium_paid_date=p['LastPremiumPaidDate'],
                next_premium_due_date=p['NextPremiumDueDate']
            )
            # Add policy_id attribute for reference
            setattr(policy, 'policy_id', p['PolicyID'])
            policies.append(policy)
        
        if policies:
            # Generate premium payments
            payments = generate_premium_payments(policies, simulation_date)
            
            # Insert the payments
            payment_dicts = [payment.to_dict() for payment in payments]
            for payment_dict in payment_dicts:
                # Add LastModified
                payment_dict['LastModified'] = simulation_date
                
                columns = ', '.join(payment_dict.keys())
                placeholders = ', '.join(['?'] * len(payment_dict))
                values = tuple(payment_dict.values())
                
                query = f"""
                INSERT INTO Insurance.PremiumPayments (
                    {columns}
                ) VALUES (
                    {placeholders}
                )
                """
                execute_non_query(query, values)
            
            # Update policies with new payment dates
            for policy in policies:
                query = """
                UPDATE Insurance.Policies
                SET LastPremiumPaidDate = ?, NextPremiumDueDate = ?, LastModified = ?
                WHERE PolicyID = ?
                """
                execute_non_query(query, (
                    policy.last_premium_paid_date, 
                    policy.next_premium_due_date,
                    simulation_date,
                    policy.policy_id
                ))
            
            # Get new count of premium payments
            new_count = execute_query("SELECT COUNT(*) AS count FROM Insurance.PremiumPayments")[0]['count']
            
            # Check that new premium payments were added
            assert new_count > initial_count
    
    def test_run_daily_simulation(self, simulation, simulation_date):
        """Test running a daily simulation."""
        # Get initial counts
        initial_members = execute_query("SELECT COUNT(*) AS count FROM Insurance.Members")[0]['count']
        initial_plans = execute_query("SELECT COUNT(*) AS count FROM Insurance.CoveragePlans")[0]['count']
        initial_policies = execute_query("SELECT COUNT(*) AS count FROM Insurance.Policies")[0]['count']
        
        # Run a daily simulation with minimal settings to avoid too many changes
        simulation.run_daily_simulation(
            simulation_date=simulation_date,
            new_members_count=2,
            add_new_plans=True,
            new_plans_count=1,
            new_providers_count=1,
            new_policies_count=1,
            hospital_claims_count=1,
            general_claims_count=2
        )
        
        # Get new counts
        new_members = execute_query("SELECT COUNT(*) AS count FROM Insurance.Members")[0]['count']
        new_plans = execute_query("SELECT COUNT(*) AS count FROM Insurance.CoveragePlans")[0]['count']
        new_policies = execute_query("SELECT COUNT(*) AS count FROM Insurance.Policies")[0]['count']
        
        # Check that new records were added
        assert new_members > initial_members
        assert new_plans > initial_plans
        assert new_policies > initial_policies
        
        # Check that the new records have the correct LastModified date
        date_filter = f"CONVERT(date, LastModified) = '{simulation_date.strftime('%Y-%m-%d')}'"
        
        new_members_count = execute_query(f"SELECT COUNT(*) AS count FROM Insurance.Members WHERE {date_filter}")[0]['count']
        new_plans_count = execute_query(f"SELECT COUNT(*) AS count FROM Insurance.CoveragePlans WHERE {date_filter}")[0]['count']
        new_policies_count = execute_query(f"SELECT COUNT(*) AS count FROM Insurance.Policies WHERE {date_filter}")[0]['count']
        
        assert new_members_count > 0
        assert new_plans_count > 0
        assert new_policies_count > 0