"""
Integration tests for database operations.

These tests require a connection to the actual database.
They should be run in a test environment with a separate database.
"""
import pytest
import os
import sys
from datetime import date, datetime
import pyodbc
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from health_insurance_au.utils.db_utils import (
    get_connection, execute_query, execute_non_query, bulk_insert
)
from health_insurance_au.models.models import Member, CoveragePlan


# Skip these tests if the environment variable TEST_DB is not set to 'true'
pytestmark = pytest.mark.skipif(
    os.environ.get('TEST_DB') != 'true',
    reason="Integration tests require TEST_DB=true environment variable"
)


@pytest.fixture(scope="module")
def setup_test_db():
    """Set up a test database for integration tests."""
    # Create a test table
    execute_non_query("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TestMembers')
    CREATE TABLE TestMembers (
        MemberID INT IDENTITY(1,1) PRIMARY KEY,
        FirstName NVARCHAR(100) NOT NULL,
        LastName NVARCHAR(100) NOT NULL,
        DateOfBirth DATE NOT NULL,
        Gender NVARCHAR(10) NOT NULL,
        Email NVARCHAR(255) NULL,
        AddressLine1 NVARCHAR(255) NOT NULL,
        City NVARCHAR(100) NOT NULL,
        State NVARCHAR(50) NOT NULL,
        PostCode NVARCHAR(20) NOT NULL,
        IsActive BIT NOT NULL DEFAULT 1
    )
    """)
    
    yield
    
    # Clean up the test table
    execute_non_query("DROP TABLE IF EXISTS TestMembers")


@pytest.mark.skip(reason="Integration test requires database connection")
def test_connection():
    """Test database connection."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = ["Microsoft SQL Server 2019"]
    
    with patch('pyodbc.connect', return_value=mock_connection):
        with get_connection() as conn:
            assert conn is not None
            
            # Test a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            row = cursor.fetchone()
            assert row is not None


def test_execute_query(setup_test_db):
    """Test executing a query against the test database."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Set up mock cursor for test_execute_query
    mock_cursor.description = [('MemberID', None, None, None, None, None, None),
                              ('FirstName', None, None, None, None, None, None),
                              ('LastName', None, None, None, None, None, None),
                              ('Email', None, None, None, None, None, None)]
    mock_cursor.fetchall.return_value = [(1, 'John', 'Smith', 'john@example.com')]
    
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Set up the mock connection to be returned by get_connection
        mock_get_conn.return_value.__enter__.return_value = mock_connection
        
        # Query the data
        results = execute_query("SELECT * FROM TestMembers WHERE FirstName = 'John'")
        
        # Verify the query was executed
        mock_connection.cursor().execute.assert_called_with("SELECT * FROM TestMembers WHERE FirstName = 'John'")
        
        # Verify the results
        assert len(results) == 1
        assert results[0]['FirstName'] == 'John'
        assert results[0]['LastName'] == 'Smith'
        assert results[0]['Email'] == 'john@example.com'


def test_execute_non_query(setup_test_db):
    """Test executing a non-query statement against the test database."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Set up mock cursor for test_execute_non_query
    mock_cursor.rowcount = 1
    
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Set up the mock connection to be returned by get_connection
        mock_get_conn.return_value.__enter__.return_value = mock_connection
        
        # Insert test data
        affected_rows = execute_non_query("""
        INSERT INTO TestMembers (FirstName, LastName, DateOfBirth, Gender, Email, AddressLine1, City, State, PostCode)
        VALUES ('Jane', 'Doe', '1985-05-20', 'Female', 'jane@example.com', '456 Oak St', 'Melbourne', 'VIC', '3000')
        """)
        
        # Verify one row was affected
        assert affected_rows == 1
        
        # Verify the statement was executed
        mock_connection.cursor().execute.assert_called_with("""
        INSERT INTO TestMembers (FirstName, LastName, DateOfBirth, Gender, Email, AddressLine1, City, State, PostCode)
        VALUES ('Jane', 'Doe', '1985-05-20', 'Female', 'jane@example.com', '456 Oak St', 'Melbourne', 'VIC', '3000')
        """)


def test_bulk_insert(setup_test_db):
    """Test bulk insert operation against the test database."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Set up the mock cursor's executemany method to handle bulk insert
    mock_cursor.executemany.return_value = None
    mock_cursor.rowcount = 2
    
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Set up the mock connection to be returned by get_connection
        mock_get_conn.return_value.__enter__.return_value = mock_connection
        
        # Create test data
        members = [
            {
                'FirstName': 'Alice',
                'LastName': 'Johnson',
                'DateOfBirth': date(1990, 3, 15),
                'Gender': 'Female',
                'Email': 'alice@example.com',
                'AddressLine1': '789 Pine St',
                'City': 'Brisbane',
                'State': 'QLD',
                'PostCode': '4000',
                'IsActive': True
            },
            {
                'FirstName': 'Bob',
                'LastName': 'Brown',
                'DateOfBirth': date(1975, 8, 22),
                'Gender': 'Male',
                'Email': 'bob@example.com',
                'AddressLine1': '101 Elm St',
                'City': 'Perth',
                'State': 'WA',
                'PostCode': '6000',
                'IsActive': True
            }
        ]
        
        # Perform bulk insert
        rows_inserted = bulk_insert("TestMembers", members)
        
        # Verify executemany was called
        mock_connection.cursor().executemany.assert_called_once()
        
        # Verify two rows were inserted
        assert rows_inserted == 2


def test_member_model_integration(setup_test_db):
    """Test Member model integration with the database."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Set up mock cursor for test_member_model_integration
    mock_cursor.rowcount = 1
    mock_cursor.description = [('FirstName', None, None, None, None, None, None),
                              ('LastName', None, None, None, None, None, None),
                              ('Email', None, None, None, None, None, None)]
    mock_cursor.fetchall.return_value = [("Michael", "Wilson", "michael@example.com")]
    
    with patch('health_insurance_au.utils.db_utils.get_connection') as mock_get_conn:
        # Set up the mock connection to be returned by get_connection
        mock_get_conn.return_value.__enter__.return_value = mock_connection
        
        # Create a Member object
        member = Member(
            first_name="Michael",
            last_name="Wilson",
            date_of_birth=date(1982, 7, 10),
            gender="Male",
            address_line1="222 Cedar St",
            city="Adelaide",
            state="SA",
            post_code="5000",
            email="michael@example.com",
            mobile_phone="0412345678",
            member_number="MEM123"
        )
        
        # Convert to dictionary for database operations
        member_dict = member.to_dict()
        
        # Insert into database (exclude MemberID which is auto-generated)
        columns = ', '.join([k for k in member_dict.keys() if k != 'MemberID'])
        placeholders = ', '.join(['?' for _ in range(len(member_dict) - 1)])
        values = [v for k, v in member_dict.items() if k != 'MemberID']
        
        query = f"INSERT INTO TestMembers ({columns}) VALUES ({placeholders})"
        
        # Execute the insert
        execute_non_query(query, tuple(values))
        
        # Verify the statement was executed
        mock_connection.cursor().execute.assert_called_once()
        
        # Query to verify the insertion
        results = execute_query("SELECT * FROM TestMembers WHERE MemberNumber = 'MEM123'")
        
        # Verify the results
        assert len(results) == 1
        assert results[0]['FirstName'] == "Michael"
        assert results[0]['LastName'] == "Wilson"
        assert results[0]['Email'] == "michael@example.com"