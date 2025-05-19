"""
Integration test for Member model.
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
from health_insurance_au.models.models import Member


class TestMemberIntegration:
    """Integration tests for Member model."""
    
    def test_create_and_retrieve_member(self):
        """Test creating and retrieving a member."""
        # Generate a unique member number
        member_number = f"TST{uuid.uuid4().hex[:8].upper()}"
        
        # Create a member
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
        
        try:
            # Convert to dictionary for database insertion
            member_dict = member.to_dict()
            
            # Add LastModified field
            member_dict['LastModified'] = date.today()
            
            # Construct SQL query
            columns = ', '.join(member_dict.keys())
            placeholders = ', '.join(['?'] * len(member_dict))
            values = tuple(member_dict.values())
            
            # Insert into database
            execute_non_query(f"""
            INSERT INTO Insurance.Members ({columns})
            VALUES ({placeholders})
            """, values)
            
            # Retrieve from database
            result = execute_query("""
            SELECT * FROM Insurance.Members WHERE MemberNumber = ?
            """, (member_number,))
            
            # Assert member was inserted correctly
            assert len(result) == 1
            assert result[0]['FirstName'] == "Test"
            assert result[0]['LastName'] == "Member"
            assert result[0]['MemberNumber'] == member_number
            
        finally:
            # Clean up
            execute_non_query("""
            DELETE FROM Insurance.Members WHERE MemberNumber = ?
            """, (member_number,))