"""
Integration tests for database operations.
"""
import pytest
from datetime import date, timedelta
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from health_insurance_au.utils.db_utils import (
    get_connection,
    execute_query,
    execute_non_query,
    execute_stored_procedure,
    bulk_insert
)


class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    def test_connection(self, db_connection):
        """Test database connection."""
        assert db_connection is not None
        
    def test_execute_query(self):
        """Test executing a query."""
        # Simple query to test connection
        result = execute_query("SELECT 1 AS TestValue")
        assert len(result) == 1
        assert result[0]['TestValue'] == 1
        
    def test_execute_query_with_params(self):
        """Test executing a query with parameters."""
        param_value = 42
        result = execute_query("SELECT ? AS TestValue", (param_value,))
        assert len(result) == 1
        assert result[0]['TestValue'] == param_value
        
    def test_execute_non_query(self):
        """Test executing a non-query statement."""
        # Create a temporary table
        execute_non_query("""
            IF OBJECT_ID('tempdb..#TempTestTable') IS NOT NULL
                DROP TABLE #TempTestTable;
            
            CREATE TABLE #TempTestTable (
                ID INT,
                Name NVARCHAR(100),
                TestDate DATE
            )
        """)
        
        # Insert a row
        today = date.today()
        execute_non_query(
            "INSERT INTO #TempTestTable (ID, Name, TestDate) VALUES (?, ?, ?)",
            (1, "Test Name", today)
        )
        
        # Query to verify
        result = execute_query("SELECT * FROM #TempTestTable")
        assert len(result) == 1
        assert result[0]['ID'] == 1
        assert result[0]['Name'] == "Test Name"
        assert result[0]['TestDate'].strftime('%Y-%m-%d') == today.strftime('%Y-%m-%d')
        
        # Clean up
        execute_non_query("DROP TABLE #TempTestTable")
        
    def test_bulk_insert(self):
        """Test bulk insert operation."""
        # Create a temporary table
        execute_non_query("""
            IF OBJECT_ID('tempdb..#BulkTestTable') IS NOT NULL
                DROP TABLE #BulkTestTable;
            
            CREATE TABLE #BulkTestTable (
                ID INT,
                Name NVARCHAR(100),
                TestDate DATE,
                LastModified DATETIME DEFAULT GETDATE()
            )
        """)
        
        # Prepare test data
        today = date.today()
        test_data = [
            {'ID': 1, 'Name': 'Test 1', 'TestDate': today},
            {'ID': 2, 'Name': 'Test 2', 'TestDate': today - timedelta(days=1)},
            {'ID': 3, 'Name': 'Test 3', 'TestDate': today - timedelta(days=2)}
        ]
        
        # Perform bulk insert
        rows_inserted = bulk_insert('#BulkTestTable', test_data)
        
        # Query to verify
        result = execute_query("SELECT * FROM #BulkTestTable ORDER BY ID")
        assert len(result) == 3
        assert result[0]['ID'] == 1
        assert result[0]['Name'] == "Test 1"
        assert result[0]['TestDate'].strftime('%Y-%m-%d') == today.strftime('%Y-%m-%d')
        
        # Clean up
        execute_non_query("DROP TABLE #BulkTestTable")