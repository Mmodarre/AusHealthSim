"""
Basic integration test for database connection.
"""
import pytest
from datetime import date
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from health_insurance_au.utils.db_utils import get_connection, execute_query


class TestBasicDatabaseIntegration:
    """Basic integration tests for database operations."""
    
    def test_connection(self):
        """Test database connection."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 AS TestValue")
            result = cursor.fetchall()
            assert len(result) == 1
            assert result[0][0] == 1
    
    def test_execute_query(self):
        """Test executing a simple query."""
        result = execute_query("SELECT 1 AS TestValue")
        assert len(result) == 1
        assert result[0]['TestValue'] == 1
    
    def test_database_schema(self):
        """Test that the expected database schema exists."""
        # Check for Insurance schema
        result = execute_query("""
        SELECT schema_id FROM sys.schemas WHERE name = 'Insurance'
        """)
        assert len(result) == 1
        
        # Check for some key tables
        tables = ['Members', 'Policies', 'CoveragePlans', 'Claims', 'PremiumPayments']
        for table in tables:
            result = execute_query(f"""
            SELECT object_id FROM sys.tables 
            WHERE name = '{table}' AND schema_id = (SELECT schema_id FROM sys.schemas WHERE name = 'Insurance')
            """)
            assert len(result) == 1, f"Table {table} not found in Insurance schema"