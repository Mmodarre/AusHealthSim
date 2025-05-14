"""
Unit tests for the data loader module.
"""
import pytest
import json
from unittest.mock import patch, mock_open
from datetime import date

from health_insurance_au.utils.data_loader import (
    load_sample_data, convert_to_members
)


@pytest.fixture
def sample_json_data():
    """Fixture for sample JSON data."""
    return [
        {
            "first_name": "John",
            "last_name": "Smith",
            "date_of_birth": "1980-01-15",
            "gender": "Male",
            "email": "john.smith@example.com",
            "mobile_phone": "0412345678",
            "address": "123 Main St",
            "city": "Sydney",
            "state": "NSW",
            "postcode": "2000"
        },
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "date_of_birth": "1985-05-20",
            "gender": "Female",
            "email": "jane.doe@example.com",
            "mobile_phone": "0498765432",
            "address": "456 Oak St",
            "city": "Melbourne",
            "state": "VIC",
            "postcode": "3000"
        }
    ]


def test_load_sample_data():
    """Test loading sample data."""
    # Mock the open function to return sample JSON data
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data=json.dumps([{"name": "Test"}]))):
        # Load sample data
        data = load_sample_data()
        
        # Verify data was loaded
        assert len(data) == 1
        assert data[0]["name"] == "Test"


def test_load_sample_data_file_not_found():
    """Test handling of file not found."""
    # Mock os.path.exists to return False
    with patch('os.path.exists', return_value=False):
        # Load sample data
        data = load_sample_data()
        
        # Verify empty list is returned
        assert data == []


def test_convert_to_members(sample_json_data):
    """Test converting JSON data to Member objects."""
    # Convert sample data to Member objects
    members = convert_to_members(sample_json_data)
    
    # Verify the correct number of members were created
    assert len(members) == 2
    
    # Verify member properties
    assert members[0].first_name == "John"
    assert members[0].last_name == "Smith"
    assert members[0].date_of_birth == date(1980, 1, 15)
    assert members[0].gender == "Male"
    assert members[0].email == "john.smith@example.com"
    assert members[0].mobile_phone == "0412345678"
    assert members[0].address_line1 == "123 Main St"
    assert members[0].city == "Sydney"
    assert members[0].state == "NSW"
    assert members[0].post_code == "2000"
    
    assert members[1].first_name == "Jane"
    assert members[1].last_name == "Doe"


def test_convert_to_members_with_count(sample_json_data):
    """Test converting JSON data to Member objects with a count limit."""
    # Convert sample data to Member objects with a limit of 1
    members = convert_to_members(sample_json_data, count=1)
    
    # Verify only one member was created
    assert len(members) == 1