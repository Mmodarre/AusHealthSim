"""
Integration tests for CDC (Change Data Capture) functionality.
"""
import pytest
from datetime import date, timedelta, datetime
import os
import sys
import uuid

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from health_insurance_au.utils.db_utils import execute_query, execute_non_query
from health_insurance_au.utils.cdc_utils import (
    get_cdc_changes,
    get_cdc_net_changes,
    list_cdc_tables
)


class TestCDCIntegration:
    """Integration tests for CDC functionality."""
    
    def test_list_cdc_tables(self):
        """Test retrieving CDC-enabled tables."""
        # Get CDC-enabled tables
        cdc_tables = list_cdc_tables()
        
        # Check that we have CDC-enabled tables
        assert len(cdc_tables) > 0
        
        # Check that the expected tables are CDC-enabled
        expected_tables = [
            'Insurance.Members',
            'Insurance.Policies',
            'Insurance.Claims',
            'Insurance.CoveragePlans',
            'Insurance.Providers',
            'Insurance.PremiumPayments'
        ]
        
        for table in expected_tables:
            table_name = table.split('.')[1].lower()
            assert any(table_name.lower() in cdc_table['table_name'].lower() for cdc_table in cdc_tables)
    
    def test_cdc_change_tracking(self, simulation_date):
        """Test CDC change tracking for a table."""
        # Create a test member
        member_number = f"CDC{uuid.uuid4().hex[:8].upper()}"
        
        # Insert a new member
        execute_non_query("""
        INSERT INTO Insurance.Members (
            MemberNumber, FirstName, LastName, DateOfBirth, Gender,
            Email, Phone, AddressLine1, Suburb, State, Postcode,
            MedicareNumber, LHCLoading, LastModified
        ) VALUES (
            ?, 'CDC', 'Test', '1990-01-01', 'M',
            'cdc.test@example.com', '0400123456', '123 CDC Street', 'Sydney', 'NSW', '2000',
            '1234567890', 0.0, GETDATE()
        )
        """, (member_number,))
        
        # Get the member ID
        member_id = execute_query(
            "SELECT MemberID FROM Insurance.Members WHERE MemberNumber = ?",
            (member_number,)
        )[0]['MemberID']
        
        # Get CDC changes for the Members table
        changes = get_cdc_changes('Insurance', 'Members')
        
        # Check that our new member is in the changes
        assert len(changes) > 0
        assert any(change['__$operation'] == 2 and change['MemberID'] == member_id for change in changes)
        
        # Update the member
        execute_non_query("""
        UPDATE Insurance.Members
        SET Email = ?, LastModified = GETDATE()
        WHERE MemberNumber = ?
        """, ('updated.cdc@example.com', member_number))
        
        # Get CDC changes again
        changes = get_cdc_changes('Insurance', 'Members')
        
        # Check that our updated member is in the changes
        assert any(change['__$operation'] == 4 and change['MemberID'] == member_id for change in changes)
        
        # Delete the member
        execute_non_query(
            "DELETE FROM Insurance.Members WHERE MemberNumber = ?",
            (member_number,)
        )
        
        # Get CDC changes again
        changes = get_cdc_changes('Insurance', 'Members')
        
        # Check that our deleted member is in the changes
        assert any(change['__$operation'] == 1 and change['MemberID'] == member_id for change in changes)
    
    def test_get_cdc_net_changes(self, simulation_date):
        """Test retrieving net changes from CDC."""
        # Create a test member
        member_number = f"NET{uuid.uuid4().hex[:8].upper()}"
        
        # Insert a new member
        execute_non_query("""
        INSERT INTO Insurance.Members (
            MemberNumber, FirstName, LastName, DateOfBirth, Gender,
            Email, Phone, AddressLine1, Suburb, State, Postcode,
            MedicareNumber, LHCLoading, LastModified
        ) VALUES (
            ?, 'Net', 'Change', '1990-01-01', 'M',
            'net.change@example.com', '0400123456', '123 Net Street', 'Sydney', 'NSW', '2000',
            '1234567890', 0.0, GETDATE()
        )
        """, (member_number,))
        
        # Get the member ID
        member_id = execute_query(
            "SELECT MemberID FROM Insurance.Members WHERE MemberNumber = ?",
            (member_number,)
        )[0]['MemberID']
        
        # Update the member multiple times
        execute_non_query("""
        UPDATE Insurance.Members
        SET Email = ?, LastModified = GETDATE()
        WHERE MemberNumber = ?
        """, ('update1@example.com', member_number))
        
        execute_non_query("""
        UPDATE Insurance.Members
        SET Email = ?, LastModified = GETDATE()
        WHERE MemberNumber = ?
        """, ('update2@example.com', member_number))
        
        execute_non_query("""
        UPDATE Insurance.Members
        SET Email = ?, LastModified = GETDATE()
        WHERE MemberNumber = ?
        """, ('final@example.com', member_number))
        
        # Get net changes
        net_changes = get_cdc_net_changes('Insurance', 'Members')
        
        # Check that our member has only one net change with the final value
        member_changes = [change for change in net_changes if change['MemberID'] == member_id]
        assert len(member_changes) == 1
        assert member_changes[0]['Email'] == 'final@example.com'
        
        # Delete the member
        execute_non_query(
            "DELETE FROM Insurance.Members WHERE MemberNumber = ?",
            (member_number,)
        )
        
        # Get net changes again
        net_changes = get_cdc_net_changes('Insurance', 'Members')
        
        # Check that our member is not in the net changes (since it was created and deleted)
        assert not any(change['MemberID'] == member_id for change in net_changes)