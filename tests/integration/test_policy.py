"""
Integration test for Policy model.
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
from health_insurance_au.models.models import Policy, Member, CoveragePlan


class TestPolicyIntegration:
    """Integration tests for Policy model."""
    
    def test_create_and_retrieve_policy(self):
        """Test creating and retrieving a policy with member relationship."""
        # First, create a member
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
        
        # Create a coverage plan
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
        
        # Create a policy
        policy_number = f"POL{uuid.uuid4().hex[:8].upper()}"
        
        try:
            # Insert member
            member_dict = member.to_dict()
            member_dict['LastModified'] = date.today()
            columns = ', '.join(member_dict.keys())
            placeholders = ', '.join(['?'] * len(member_dict))
            values = tuple(member_dict.values())
            execute_non_query(f"""
            INSERT INTO Insurance.Members ({columns})
            VALUES ({placeholders})
            """, values)
            
            # Get member ID
            member_result = execute_query("""
            SELECT MemberID FROM Insurance.Members WHERE MemberNumber = ?
            """, (member_number,))
            member_id = member_result[0]['MemberID']
            
            # Insert coverage plan
            plan_dict = plan.to_dict()
            plan_dict['LastModified'] = date.today()
            columns = ', '.join(plan_dict.keys())
            placeholders = ', '.join(['?'] * len(plan_dict))
            values = tuple(plan_dict.values())
            execute_non_query(f"""
            INSERT INTO Insurance.CoveragePlans ({columns})
            VALUES ({placeholders})
            """, values)
            
            # Get plan ID
            plan_result = execute_query("""
            SELECT PlanID FROM Insurance.CoveragePlans WHERE PlanCode = ?
            """, (plan_code,))
            plan_id = plan_result[0]['PlanID']
            
            # Create policy object
            policy = Policy(
                policy_number=policy_number,
                primary_member_id=member_id,
                plan_id=plan_id,
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
            
            # Insert policy
            policy_dict = policy.to_dict()
            policy_dict['LastModified'] = date.today()
            columns = ', '.join(policy_dict.keys())
            placeholders = ', '.join(['?'] * len(policy_dict))
            values = tuple(policy_dict.values())
            execute_non_query(f"""
            INSERT INTO Insurance.Policies ({columns})
            VALUES ({placeholders})
            """, values)
            
            # Get policy ID
            policy_result = execute_query("""
            SELECT PolicyID FROM Insurance.Policies WHERE PolicyNumber = ?
            """, (policy_number,))
            policy_id = policy_result[0]['PolicyID']
            
            # Create policy member relationship
            execute_non_query("""
            INSERT INTO Insurance.PolicyMembers (
                PolicyID, MemberID, RelationshipToPrimary, StartDate, IsActive, LastModified
            ) VALUES (
                ?, ?, 'Self', ?, 1, ?
            )
            """, (policy_id, member_id, date.today(), date.today()))
            
            # Retrieve policy with member
            result = execute_query("""
            SELECT p.*, m.FirstName, m.LastName, m.MemberNumber
            FROM Insurance.Policies p
            JOIN Insurance.PolicyMembers pm ON p.PolicyID = pm.PolicyID
            JOIN Insurance.Members m ON pm.MemberID = m.MemberID
            WHERE p.PolicyNumber = ?
            """, (policy_number,))
            
            # Assert policy was inserted correctly
            assert len(result) == 1
            assert result[0]['PolicyNumber'] == policy_number
            assert result[0]['PrimaryMemberID'] == member_id
            assert result[0]['PlanID'] == plan_id
            assert result[0]['Status'] == "Active"
            assert result[0]['FirstName'] == "Test"
            assert result[0]['LastName'] == "Member"
            assert result[0]['MemberNumber'] == member_number
            
        finally:
            # Clean up - delete in reverse order of creation
            execute_non_query("""
            DELETE FROM Insurance.PolicyMembers WHERE PolicyID IN (
                SELECT PolicyID FROM Insurance.Policies WHERE PolicyNumber = ?
            )
            """, (policy_number,))
            
            execute_non_query("""
            DELETE FROM Insurance.Policies WHERE PolicyNumber = ?
            """, (policy_number,))
            
            execute_non_query("""
            DELETE FROM Insurance.CoveragePlans WHERE PlanCode = ?
            """, (plan_code,))
            
            execute_non_query("""
            DELETE FROM Insurance.Members WHERE MemberNumber = ?
            """, (member_number,))