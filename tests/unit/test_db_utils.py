"""
Unit tests for the database utilities.
"""
import pytest
from unittest.mock import patch, MagicMock, call
import sys

# Import the conftest module to ensure the pyodbc mock is set up
from tests.conftest import *

from health_insurance_au.utils.db_utils import (
    get_connection, execute_query, execute_non_query, 
    execute_stored_procedure, bulk_insert
)


def test_get_connection():
    """Test the get_connection context manager."""
    # Create mock connection
    mock_conn = MagicMock()
    
    # Mock pyodbc.connect to return our mock connection
    with patch('health_insurance_au.utils.db_utils.pyodbc.connect', return_value=mock_conn) as mock_connect:
        # Use the context manager
        with get_connection() as conn:
            assert conn is mock_conn
        
        # Verify the connection was closed
        mock_conn.close.assert_called_once()


def test_get_connection_error():
    """Test handling of connection errors."""
    # Create a mock error
    mock_error = Exception("Connection failed")
    
    # Mock pyodbc.connect to raise an exception
    with patch('health_insurance_au.utils.db_utils.pyodbc.connect', side_effect=mock_error):
        # Use the context manager and expect an exception
        with pytest.raises(Exception) as excinfo:
            with get_connection():
                pass
        
        # Verify the exception was raised
        assert "Connection failed" in str(excinfo.value)


def test_execute_query():
    """Test executing a query."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Set up cursor description and fetchall
    mock_cursor.description = [('id', None, None, None, None, None, None), 
                              ('name', None, None, None, None, None, None)]
    mock_cursor.fetchall.return_value = [(1, 'John'), (2, 'Jane')]
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute the query
        results = execute_query("SELECT id, name FROM Members")
        
        # Verify the query was executed
        mock_cursor.execute.assert_called_once_with("SELECT id, name FROM Members")
        
        # Verify the results were processed correctly
        assert len(results) == 2
        assert results[0]['id'] == 1
        assert results[0]['name'] == 'John'
        assert results[1]['id'] == 2
        assert results[1]['name'] == 'Jane'


def test_execute_query_with_params():
    """Test executing a query with parameters."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Set up cursor description and fetchall
    mock_cursor.description = [('id', None, None, None, None, None, None), 
                              ('name', None, None, None, None, None, None)]
    mock_cursor.fetchall.return_value = [(1, 'John')]
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute the query with parameters
        results = execute_query("SELECT id, name FROM Members WHERE id = ?", (1,))
        
        # Verify the query was executed with parameters
        mock_cursor.execute.assert_called_once_with("SELECT id, name FROM Members WHERE id = ?", (1,))
        
        # Verify the results were processed correctly
        assert len(results) == 1
        assert results[0]['id'] == 1
        assert results[0]['name'] == 'John'


def test_execute_query_no_results():
    """Test executing a query with no results."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Set up cursor with no description (no columns)
    mock_cursor.description = None
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute the query
        results = execute_query("SELECT id, name FROM Members WHERE id = 999")
        
        # Verify the query was executed
        mock_cursor.execute.assert_called_once_with("SELECT id, name FROM Members WHERE id = 999")
        
        # Verify empty results
        assert results == []


def test_execute_query_error():
    """Test handling of query execution errors."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Set up cursor to raise an exception
    mock_cursor.execute.side_effect = Exception('Query failed')
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute the query
        results = execute_query("SELECT * FROM NonExistentTable")
        
        # Verify empty results on error
        assert results == []


def test_execute_non_query():
    """Test executing a non-query statement."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Set up cursor with rowcount
    mock_cursor.rowcount = 5
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute the non-query
        affected_rows = execute_non_query("UPDATE Members SET active = 1")
        
        # Verify the statement was executed
        mock_cursor.execute.assert_called_once_with("UPDATE Members SET active = 1")
        
        # Verify the affected rows count
        assert affected_rows == 5


def test_execute_non_query_with_params():
    """Test executing a non-query statement with parameters."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Set up cursor with rowcount
    mock_cursor.rowcount = 1
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute the non-query with parameters
        affected_rows = execute_non_query("UPDATE Members SET active = ? WHERE id = ?", (1, 5))
        
        # Verify the statement was executed with parameters
        mock_cursor.execute.assert_called_once_with("UPDATE Members SET active = ? WHERE id = ?", (1, 5))
        
        # Verify the affected rows count
        assert affected_rows == 1


def test_execute_non_query_error():
    """Test handling of non-query execution errors."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Set up cursor to raise an exception
    mock_cursor.execute.side_effect = Exception('Update failed')
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute the non-query
        affected_rows = execute_non_query("UPDATE NonExistentTable SET field = 1")
        
        # Verify zero affected rows on error
        assert affected_rows == 0


def test_execute_stored_procedure():
    """Test executing a stored procedure."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Set up cursor description and fetchall
    mock_cursor.description = [('id', None, None, None, None, None, None), 
                              ('name', None, None, None, None, None, None)]
    mock_cursor.fetchall.return_value = [(1, 'John'), (2, 'Jane')]
    mock_cursor.nextset.return_value = False  # No more result sets
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute the stored procedure
        results = execute_stored_procedure("GetMembers")
        
        # Verify the stored procedure was executed
        mock_cursor.execute.assert_called_once_with("EXEC GetMembers")
        
        # Verify the results were processed correctly
        assert len(results) == 2
        assert results[0]['id'] == 1
        assert results[0]['name'] == 'John'
        assert results[1]['id'] == 2
        assert results[1]['name'] == 'Jane'


def test_execute_stored_procedure_with_params():
    """Test executing a stored procedure with parameters."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Set up cursor description and fetchall
    mock_cursor.description = [('id', None, None, None, None, None, None), 
                              ('name', None, None, None, None, None, None)]
    mock_cursor.fetchall.return_value = [(1, 'John')]
    mock_cursor.nextset.return_value = False  # No more result sets
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute the stored procedure with parameters
        results = execute_stored_procedure("GetMemberById", {'id': 1})
        
        # Verify the stored procedure was executed with parameters
        mock_cursor.execute.assert_called_once_with("EXEC GetMemberById @id=?", [1])
        
        # Verify the results were processed correctly
        assert len(results) == 1
        assert results[0]['id'] == 1
        assert results[0]['name'] == 'John'


def test_execute_stored_procedure_multiple_result_sets():
    """Test executing a stored procedure with multiple result sets."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Create a more complex mock for description that changes between result sets
    description1 = [('id', None, None, None, None, None, None), 
                   ('name', None, None, None, None, None, None)]
    description2 = [('id', None, None, None, None, None, None), 
                   ('name', None, None, None, None, None, None)]
    
    # Configure description to change after nextset is called
    mock_cursor.description = description1
    
    # Configure fetchall to return different results for each call
    mock_cursor.fetchall.side_effect = [
        [(1, 'John')],  # First result set
        [(101, 'POL-001')]  # Second result set
    ]
    
    # Configure nextset to return True first (indicating there's another result set)
    # Then False (indicating no more result sets)
    def side_effect_nextset():
        # Change description after first nextset call
        mock_cursor.description = description2
        return True
    
    mock_cursor.nextset.side_effect = [side_effect_nextset, False]
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute the stored procedure
        results = execute_stored_procedure("GetMemberWithPolicies", {'id': 1})
        
        # Verify the stored procedure was executed
        mock_cursor.execute.assert_called_once_with("EXEC GetMemberWithPolicies @id=?", [1])
        
        # Verify the results were processed correctly
        assert len(results) == 2
        assert results[0]['id'] == 1
        assert results[0]['name'] == 'John'
        assert results[1]['id'] == 101
        assert results[1]['name'] == 'POL-001'


def test_execute_stored_procedure_error():
    """Test handling of stored procedure execution errors."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Set up cursor to raise an exception
    mock_cursor.execute.side_effect = Exception('Procedure failed')
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute the stored procedure
        results = execute_stored_procedure("NonExistentProcedure")
        
        # Verify empty results on error
        assert results == []


def test_bulk_insert():
    """Test bulk insert operation."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock cursor.fetchone() to return None for the LastModified check
    mock_cursor.fetchone.return_value = None
    
    # Prepare test data
    data = [
        {'id': 1, 'name': 'John', 'age': 30},
        {'id': 2, 'name': 'Jane', 'age': 25},
        {'id': 3, 'name': 'Bob', 'age': 40}
    ]
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute bulk insert
        rows_inserted = bulk_insert("Members", data)
        
        # Verify executemany was called
        mock_cursor.executemany.assert_called_once()
        
        # Get the call arguments
        call_args = mock_cursor.executemany.call_args[0]
        
        # Check SQL statement format (order of columns may vary)
        assert "INSERT INTO Members" in call_args[0]
        assert "VALUES" in call_args[0]
        
        # Check that the parameter sets match our data
        param_sets = call_args[1]
        assert len(param_sets) == 3
        assert (1, 'John', 30) in param_sets
        assert (2, 'Jane', 25) in param_sets
        assert (3, 'Bob', 40) in param_sets
        
        # Verify the number of inserted rows
        assert rows_inserted == 3


def test_bulk_insert_empty_data():
    """Test bulk insert with empty data."""
    # Execute bulk insert with empty data
    rows_inserted = bulk_insert("Members", [])
    
    # Verify zero rows inserted
    assert rows_inserted == 0


def test_bulk_insert_error():
    """Test handling of bulk insert errors."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock cursor.fetchone() to return None for the LastModified check
    mock_cursor.fetchone.return_value = None
    
    # Set up cursor to raise an exception
    mock_cursor.executemany.side_effect = Exception('Bulk insert failed')
    
    # Prepare test data
    data = [
        {'id': 1, 'name': 'John', 'age': 30},
        {'id': 2, 'name': 'Jane', 'age': 25}
    ]
    
    # Mock the get_connection context manager
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Mock the __enter__ and __exit__ methods of the context manager
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Execute bulk insert
        rows_inserted = bulk_insert("Members", data)
        
        # Verify zero rows inserted on error
        assert rows_inserted == 0