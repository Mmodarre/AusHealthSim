"""
Integration tests for models and their database interactions.
"""
import pytest
from datetime import date, timedelta
import os
import sys
import uuid
import random

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from health_insurance_au.utils.db_utils import execute_query, execute_non_query
from health_insurance_au.models.models import Member, Policy, CoveragePlan


class TestModelIntegration:
    """Integration tests for models and their database interactions."""
    
    @pytest.fixture
    def test_member(self):
        """Create a test member for testing."""
        # Generate a unique member number
        member_number = f"TST{uuid.uuid4().hex[:8].upper()}"
        
        member = Member(
            first_name="Test",
            last_name="Member",
            date_of_birth=date(1980, 1, 1),
            gender="M",
            address_line1="123 Test Street",
            city="Sydney",
            state="NSW",
            post_code="2000",
            member_number=member_number,
            email="test.member@example.com",
            mobile_phone="0400123456",
            home_phone="",
            medicare_number="1234567890",
            lhc_loading_percentage=0.0
        )
        
        # Insert the member into the database
        member_data = member.to_dict()
        
        columns = ', '.join(member_data.keys())
        placeholders = ', '.join(['?'] * len(member_data))
        values = tuple(member_data.values())
        
        query = f"""
        INSERT INTO Insurance.Members (
            {columns}, LastModified
        ) VALUES (
            {placeholders}, GETDATE()
        );
        SELECT SCOPE_IDENTITY() AS member_id;
        """
        
        result = execute_query(query, values)
        member_id = int(result[0]['member_id'])
        
        yield {'member': member, 'member_id': member_id, 'member_number': member_number}
        
        # Clean up
        execute_non_query(
            "DELETE FROM Insurance.Members WHERE MemberNumber = ?",
            (member_number,)
        )
    
    @pytest.fixture
    def test_coverage_plan(self):
        """Create a test coverage plan for testing."""
        # Generate a unique plan code
        plan_code = f"TST{uuid.uuid4().hex[:8].upper()}"
        
        plan = CoveragePlan(
            plan_code=plan_code,
            plan_name="Test Plan",
            plan_type="Combined",
            monthly_premium=150.0,
            annual_premium=1800.0,
            effective_date=date.today() - timedelta(days=30),
            hospital_tier="Silver",
            excess_options=[250, 500, 750],
            waiting_periods={"general": 2, "pre_existing": 12, "pregnancy": 12},
            coverage_details={"description": "Test plan for integration testing"}
        )
        
        # Insert the plan into the database
        plan_data = plan.to_dict()
        
        columns = ', '.join(plan_data.keys())
        placeholders = ', '.join(['?'] * len(plan_data))
        values = tuple(plan_data.values())
        
        query = f"""
        INSERT INTO Insurance.CoveragePlans (
            {columns}, LastModified
        ) VALUES (
            {placeholders}, GETDATE()
        );
        SELECT SCOPE_IDENTITY() AS plan_id;
        """
        
        result = execute_query(query, values)
        plan_id = int(result[0]['plan_id'])
        
        yield {'plan': plan, 'plan_id': plan_id, 'plan_code': plan_code}
        
        # Clean up
        execute_non_query(
            "DELETE FROM Insurance.CoveragePlans WHERE PlanCode = ?",
            (plan_code,)
        )
    
    @pytest.fixture
    def test_policy(self, test_member, test_coverage_plan):
        """Create a test policy for testing."""
        # Generate a unique policy number
        policy_number = f"POL{uuid.uuid4().hex[:8].upper()}"
        
        policy = Policy(
            policy_number=policy_number,
            primary_member_id=test_member['member_id'],
            plan_id=test_coverage_plan['plan_id'],
            coverage_type="Single",
            start_date=date.today() - timedelta(days=15),
            current_premium=150.0,
            premium_frequency="Monthly",
            excess_amount=500.0,
            rebate_percentage=8.2,
            lhc_loading_percentage=0.0,
            status="Active",
            payment_method="Direct Debit",
            last_premium_paid_date=date.today() - timedelta(days=15),
            next_premium_due_date=date.today() + timedelta(days=15)
        )
        
        # Insert the policy into the database
        policy_data = policy.to_dict()
        
        columns = ', '.join(policy_data.keys())
        placeholders = ', '.join(['?'] * len(policy_data))
        values = tuple(policy_data.values())
        
        query = f"""
        INSERT INTO Insurance.Policies (
            {columns}, LastModified
        ) VALUES (
            {placeholders}, GETDATE()
        );
        SELECT SCOPE_IDENTITY() AS policy_id;
        """
        
        result = execute_query(query, values)
        policy_id = int(result[0]['policy_id'])
        
        # Link member to policy
        execute_non_query("""
        INSERT INTO Insurance.PolicyMembers (
            PolicyID, MemberID, RelationshipToPrimary, StartDate, IsActive, LastModified
        ) VALUES (
            ?, ?, 'Self', GETDATE(), 1, GETDATE()
        )
        """, (policy_id, test_member['member_id']))
        
        yield {'policy': policy, 'policy_id': policy_id, 'policy_number': policy_number}
        
        # Clean up
        execute_non_query(
            "DELETE FROM Insurance.PolicyMembers WHERE PolicyID = ?",
            (policy_id,)
        )
        execute_non_query(
            "DELETE FROM Insurance.Policies WHERE PolicyNumber = ?",
            (policy_number,)
        )
    
    def test_retrieve_member(self, test_member):
        """Test retrieving a member from the database."""
        # Retrieve the member from the database
        result = execute_query(
            "SELECT * FROM Insurance.Members WHERE MemberNumber = ?",
            (test_member['member_number'],)
        )
        
        assert len(result) == 1
        assert result[0]['MemberNumber'] == test_member['member_number']
        assert result[0]['FirstName'] == test_member['member'].first_name
        assert result[0]['LastName'] == test_member['member'].last_name
    
    def test_retrieve_coverage_plan(self, test_coverage_plan):
        """Test retrieving a coverage plan from the database."""
        # Retrieve the plan from the database
        result = execute_query(
            "SELECT * FROM Insurance.CoveragePlans WHERE PlanCode = ?",
            (test_coverage_plan['plan_code'],)
        )
        
        assert len(result) == 1
        assert result[0]['PlanCode'] == test_coverage_plan['plan_code']
        assert result[0]['PlanName'] == test_coverage_plan['plan'].plan_name
        assert result[0]['PlanType'] == test_coverage_plan['plan'].plan_type
    
    def test_retrieve_policy(self, test_policy):
        """Test retrieving a policy from the database."""
        # Retrieve the policy from the database
        result = execute_query(
            "SELECT * FROM Insurance.Policies WHERE PolicyNumber = ?",
            (test_policy['policy_number'],)
        )
        
        assert len(result) == 1
        assert result[0]['PolicyNumber'] == test_policy['policy_number']
        assert result[0]['PlanID'] == test_policy['policy'].plan_id
        assert result[0]['Status'] == test_policy['policy'].status
    
    def test_policy_member_relationship(self, test_member, test_policy):
        """Test the relationship between policies and members."""
        # Retrieve the policy-member relationship from the database
        result = execute_query("""
        SELECT m.MemberNumber, p.PolicyNumber, pm.RelationshipToPrimary, pm.IsActive
        FROM Insurance.PolicyMembers pm
        JOIN Insurance.Members m ON pm.MemberID = m.MemberID
        JOIN Insurance.Policies p ON pm.PolicyID = p.PolicyID
        WHERE p.PolicyID = ? AND m.MemberID = ?
        """, (test_policy['policy_id'], test_member['member_id']))
        
        assert len(result) == 1
        assert result[0]['MemberNumber'] == test_member['member_number']
        assert result[0]['PolicyNumber'] == test_policy['policy_number']
        assert result[0]['RelationshipToPrimary'] == 'Self'
        assert result[0]['IsActive'] == True