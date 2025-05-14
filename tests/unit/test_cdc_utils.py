"""
Unit tests for the CDC utilities.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from datetime import datetime, timedelta

# Import the conftest module to ensure the pyodbc mock is set up
from tests.conftest import *

from health_insurance_au.utils.cdc_utils import (
    get_cdc_changes, get_cdc_net_changes, list_cdc_tables
)


def test_list_cdc_tables():
    """Test listing CDC-enabled tables."""
    # Set up mock for execute_query
    with patch('health_insurance_au.utils.cdc_utils.execute_query') as mock_execute_query:
        # Set up mock return value
        mock_execute_query.return_value = [
            {'schema_name': 'Insurance', 'table_name': 'Members', 'capture_instance': 'Insurance_Members'},
            {'schema_name': 'Insurance', 'table_name': 'Policies', 'capture_instance': 'Insurance_Policies'},
            {'schema_name': 'Insurance', 'table_name': 'Claims', 'capture_instance': 'Insurance_Claims'}
        ]
        
        # Call the function
        tables = list_cdc_tables()
        
        # Verify the function called execute_query with the correct SQL
        mock_execute_query.assert_called_once()
        query = mock_execute_query.call_args[0][0]
        assert "sys.tables" in query
        assert "sys.schemas" in query
        assert "is_tracked_by_cdc = 1" in query
        
        # Verify the results
        assert len(tables) == 3
        assert tables[0]['schema_name'] == 'Insurance'
        assert tables[0]['table_name'] == 'Members'
        assert tables[1]['schema_name'] == 'Insurance'
        assert tables[1]['table_name'] == 'Policies'


def test_get_cdc_changes():
    """Test getting CDC changes."""
    # Set up mock for execute_query
    with patch('health_insurance_au.utils.cdc_utils.execute_query') as mock_execute_query:
        # Set up side effect to return different results for each query
        mock_execute_query.side_effect = [
            # First call - get LSN range
            [{'from_lsn': '0x00000000000100000000', 'to_lsn': '0x00000000000200000000'}],
            # Second call - get capture instance
            [{'capture_instance': 'Insurance_Members'}],
            # Third call - get changes
            [
                {'__$start_lsn': b'\x00\x00\x00\x00\x00\x01\x00\x00', '__$end_lsn': b'\x00\x00\x00\x00\x00\x02\x00\x00',
                 '__$seqval': b'\x00\x00\x00\x00\x00\x00\x00\x01', '__$operation': 2, '__$update_mask': b'\x07',
                 'MemberID': 1, 'FirstName': 'John', 'LastName': 'Smith'},
                {'__$start_lsn': b'\x00\x00\x00\x00\x00\x01\x00\x00', '__$end_lsn': b'\x00\x00\x00\x00\x00\x02\x00\x00',
                 '__$seqval': b'\x00\x00\x00\x00\x00\x00\x00\x01', '__$operation': 4, '__$update_mask': b'\x07',
                 'MemberID': 1, 'FirstName': 'John', 'LastName': 'Doe'}
            ]
        ]
        
        # Call the function with a specific time range
        from_time = datetime.now() - timedelta(days=1)
        to_time = datetime.now()
        
        changes = get_cdc_changes('Insurance', 'Members', from_time, to_time)
        
        # Verify the function called execute_query three times
        assert mock_execute_query.call_count == 3
        
        # Check the first call - LSN query
        lsn_query = mock_execute_query.call_args_list[0][0][0]
        assert "sys.fn_cdc_map_time_to_lsn" in lsn_query
        
        # Check the second call - instance query
        instance_query = mock_execute_query.call_args_list[1][0][0]
        assert "cdc.change_tables" in instance_query
        assert "Insurance" in instance_query
        assert "Members" in instance_query
        
        # Check the third call - changes query
        changes_query = mock_execute_query.call_args_list[2][0][0]
        assert "cdc.fn_cdc_get_all_changes_" in changes_query
        assert "Insurance_Members" in changes_query
        
        # Verify the results
        assert len(changes) == 2
        
        # Check first change (insert)
        assert changes[0]['__$operation'] == 2
        assert changes[0]['MemberID'] == 1
        assert changes[0]['FirstName'] == 'John'
        assert changes[0]['LastName'] == 'Smith'
        
        # Check second change (update after)
        assert changes[1]['__$operation'] == 4
        assert changes[1]['MemberID'] == 1
        assert changes[1]['FirstName'] == 'John'
        assert changes[1]['LastName'] == 'Doe'


def test_get_cdc_changes_with_from_lsn():
    """Test getting CDC changes with a specific time range."""
    # Set up mock for execute_query
    with patch('health_insurance_au.utils.cdc_utils.execute_query') as mock_execute_query:
        # Set up side effect to return different results for each query
        mock_execute_query.side_effect = [
            # First call - get LSN range
            [{'from_lsn': '0x00000000000100000000', 'to_lsn': '0x00000000000200000000'}],
            # Second call - get capture instance
            [{'capture_instance': 'Insurance_Members'}],
            # Third call - get changes
            [
                {'__$start_lsn': b'\x00\x00\x00\x00\x00\x01\x00\x00', '__$operation': 2,
                 'MemberID': 1, 'FirstName': 'John', 'LastName': 'Smith'}
            ]
        ]
        
        # Call the function with a specific time range
        from_time = datetime(2023, 1, 1)
        to_time = datetime(2023, 1, 2)
        
        changes = get_cdc_changes('Insurance', 'Members', from_time, to_time)
        
        # Verify the function called execute_query three times
        assert mock_execute_query.call_count == 3
        
        # Verify the results
        assert len(changes) == 1
        assert changes[0]['MemberID'] == 1
        assert changes[0]['FirstName'] == 'John'
        assert changes[0]['LastName'] == 'Smith'


def test_get_cdc_net_changes():
    """Test getting CDC net changes."""
    # Set up mock for execute_query
    with patch('health_insurance_au.utils.cdc_utils.execute_query') as mock_execute_query:
        # Set up side effect to return different results for each query
        mock_execute_query.side_effect = [
            # First call - get LSN range
            [{'from_lsn': '0x00000000000100000000', 'to_lsn': '0x00000000000200000000'}],
            # Second call - get capture instance
            [{'capture_instance': 'Insurance_Members'}],
            # Third call - get net changes
            [
                {'__$start_lsn': b'\x00\x00\x00\x00\x00\x01\x00\x00', '__$operation': 1,
                 'MemberID': 1, 'FirstName': 'John', 'LastName': 'Smith'},
                {'__$start_lsn': b'\x00\x00\x00\x00\x00\x01\x00\x00', '__$operation': 2,
                 'MemberID': 2, 'FirstName': 'Jane', 'LastName': 'Doe'}
            ]
        ]
        
        # Call the function with a specific time range
        from_time = datetime(2023, 1, 1)
        to_time = datetime(2023, 1, 2)
        
        changes = get_cdc_net_changes('Insurance', 'Members', from_time, to_time)
        
        # Verify the function called execute_query three times
        assert mock_execute_query.call_count == 3
        
        # Check the first call - LSN query
        lsn_query = mock_execute_query.call_args_list[0][0][0]
        assert "sys.fn_cdc_map_time_to_lsn" in lsn_query
        
        # Check the second call - instance query
        instance_query = mock_execute_query.call_args_list[1][0][0]
        assert "cdc.change_tables" in instance_query
        
        # Check the third call - net changes query
        changes_query = mock_execute_query.call_args_list[2][0][0]
        assert "cdc.fn_cdc_get_net_changes_" in changes_query
        
        # Verify the results
        assert len(changes) == 2
        
        # Check first change (delete)
        assert changes[0]['__$operation'] == 1
        assert changes[0]['MemberID'] == 1
        assert changes[0]['FirstName'] == 'John'
        assert changes[0]['LastName'] == 'Smith'
        
        # Check second change (insert)
        assert changes[1]['__$operation'] == 2
        assert changes[1]['MemberID'] == 2
        assert changes[1]['FirstName'] == 'Jane'
        assert changes[1]['LastName'] == 'Doe'


def test_get_cdc_changes_no_lsn_range():
    """Test handling when LSN range query returns no results."""
    # Set up mock for execute_query
    with patch('health_insurance_au.utils.cdc_utils.execute_query') as mock_execute_query:
        # Set up side effect to return empty results for LSN range query
        mock_execute_query.return_value = []
        
        # Call the function
        changes = get_cdc_changes('Insurance', 'Members')
        
        # Verify the function called execute_query once
        mock_execute_query.assert_called_once()
        
        # Verify empty results
        assert changes == []


def test_get_cdc_changes_no_capture_instance():
    """Test handling when capture instance query returns no results."""
    # Set up mock for execute_query
    with patch('health_insurance_au.utils.cdc_utils.execute_query') as mock_execute_query:
        # Set up side effect to return different results for each query
        mock_execute_query.side_effect = [
            # First call - get LSN range
            [{'from_lsn': '0x00000000000100000000', 'to_lsn': '0x00000000000200000000'}],
            # Second call - get capture instance (empty result)
            []
        ]
        
        # Call the function
        changes = get_cdc_changes('Insurance', 'Members')
        
        # Verify the function called execute_query twice
        assert mock_execute_query.call_count == 2
        
        # Verify empty results
        assert changes == []


def test_get_cdc_net_changes_invalid_lsn():
    """Test handling when LSN range query returns invalid LSNs."""
    # Set up mock for execute_query
    with patch('health_insurance_au.utils.cdc_utils.execute_query') as mock_execute_query:
        # Set up side effect to return invalid LSN values
        mock_execute_query.return_value = [{'from_lsn': None, 'to_lsn': None}]
        
        # Call the function
        changes = get_cdc_net_changes('Insurance', 'Members')
        
        # Verify the function called execute_query once
        mock_execute_query.assert_called_once()
        
        # Verify empty results
        assert changes == []