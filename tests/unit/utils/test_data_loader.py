"""
Unit tests for data loading utilities.
"""
import pytest
import json
import os
from unittest.mock import patch, mock_open, MagicMock
from datetime import date, timedelta

from health_insurance_au.utils.data_loader import load_sample_data, convert_to_members
from health_insurance_au.models.models import Member

class TestDataLoader:
    """Tests for data loading utilities."""
    
    @patch('health_insurance_au.utils.data_loader.os.path.exists')
    @patch('health_insurance_au.utils.data_loader.open', new_callable=mock_open)
    @patch('health_insurance_au.utils.data_loader.json.load')
    def test_load_sample_data_success(self, mock_json_load, mock_file_open, mock_exists):
        """Test loading sample data successfully."""
        # Arrange
        mock_exists.return_value = True
        mock_json_load.return_value = [
            {'first_name': 'John', 'last_name': 'Doe'},
            {'first_name': 'Jane', 'last_name': 'Smith'}
        ]
        
        # Act
        result = load_sample_data()
        
        # Assert
        mock_exists.assert_called_once()
        mock_file_open.assert_called_once()
        mock_json_load.assert_called_once()
        
        assert len(result) == 2
        assert result[0]['first_name'] == 'John'
        assert result[1]['first_name'] == 'Jane'
    
    @patch('health_insurance_au.utils.data_loader.os.path.exists')
    def test_load_sample_data_file_not_found(self, mock_exists):
        """Test loading sample data when the file doesn't exist."""
        # Arrange
        mock_exists.return_value = False
        
        # Act
        result = load_sample_data()
        
        # Assert
        mock_exists.assert_called_once()
        assert result == []
    
    @patch('health_insurance_au.utils.data_loader.os.path.exists')
    @patch('health_insurance_au.utils.data_loader.open')
    def test_load_sample_data_exception(self, mock_open, mock_exists):
        """Test loading sample data when an exception occurs."""
        # Arrange
        mock_exists.return_value = True
        mock_open.side_effect = Exception("Test exception")
        
        # Act
        result = load_sample_data()
        
        # Assert
        mock_exists.assert_called_once()
        mock_open.assert_called_once()
        assert result == []
    
    @patch('health_insurance_au.utils.data_loader.get_unused_members')
    def test_convert_to_members_with_count(self, mock_get_unused):
        """Test converting sample data to Member objects with a count."""
        # Arrange
        sample_data = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'date_of_birth': '1980-01-01',
                'gender': 'Male',
                'address': '123 Main St',
                'city': 'Sydney',
                'state': 'NSW',
                'postcode': '2000',
                'member_id': 'M12345',
                'email': 'john.doe@example.com',
                'mobile_phone': '0412345678'
            },
            {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'date_of_birth': '1985-05-15',
                'gender': 'Female',
                'address': '456 High St',
                'city': 'Melbourne',
                'state': 'VIC',
                'postcode': '3000',
                'member_id': 'M67890',
                'email': 'jane.smith@example.com',
                'mobile_phone': '0487654321'
            }
        ]
        
        # Mock get_unused_members to return a subset of the data
        mock_get_unused.return_value = [sample_data[0]]
        
        # Act
        result = convert_to_members(sample_data, 1)
        
        # Assert
        mock_get_unused.assert_called_once_with(sample_data, 1)
        
        assert len(result) == 1
        assert isinstance(result[0], Member)
        assert result[0].first_name == 'John'
        assert result[0].last_name == 'Doe'
        assert result[0].date_of_birth == date(1980, 1, 1)
        assert result[0].gender == 'Male'
        assert result[0].address_line1 == '123 Main St'
        assert result[0].city == 'Sydney'
        assert result[0].state == 'NSW'
        assert result[0].post_code == '2000'
        assert result[0].member_number == 'M12345'
        assert result[0].email == 'john.doe@example.com'
        assert result[0].mobile_phone == '0412345678'
    
    def test_convert_to_members_without_count(self):
        """Test converting sample data to Member objects without a count."""
        # Arrange
        sample_data = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'date_of_birth': '1980-01-01',
                'gender': 'Male',
                'address': '123 Main St',
                'city': 'Sydney',
                'state': 'NSW',
                'postcode': '2000',
                'member_id': 'M12345',
                'email': 'john.doe@example.com',
                'mobile_phone': '0412345678'
            }
        ]
        
        # Act
        result = convert_to_members(sample_data)
        
        # Assert
        assert len(result) == 1
        assert isinstance(result[0], Member)
        assert result[0].first_name == 'John'
        assert result[0].last_name == 'Doe'
        assert result[0].date_of_birth == date(1980, 1, 1)
        assert result[0].gender == 'Male'
        assert result[0].address_line1 == '123 Main St'
        assert result[0].city == 'Sydney'
        assert result[0].state == 'NSW'
        assert result[0].post_code == '2000'
        assert result[0].member_number == 'M12345'
        assert result[0].email == 'john.doe@example.com'
        assert result[0].mobile_phone == '0412345678'
    
    def test_convert_to_members_missing_fields(self):
        """Test converting sample data with missing fields."""
        # Arrange
        sample_data = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                # Missing date_of_birth
                'gender': 'Male',
                # Missing address
                'city': 'Sydney',
                'state': 'NSW',
                # Missing postcode
            }
        ]
        
        # Act
        result = convert_to_members(sample_data)
        
        # Assert
        assert len(result) == 1
        assert isinstance(result[0], Member)
        assert result[0].first_name == 'John'
        assert result[0].last_name == 'Doe'
        assert result[0].date_of_birth is None
        assert result[0].gender == 'Male'
        assert result[0].address_line1 == ''
        assert result[0].city == 'Sydney'
        assert result[0].state == 'NSW'
        assert result[0].post_code == ''
    
    def test_convert_to_members_exception(self):
        """Test converting sample data when an exception occurs."""
        # Arrange
        sample_data = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'date_of_birth': 'invalid-date',  # This will cause an exception
                'gender': 'Male',
                'address': '123 Main St',
                'city': 'Sydney',
                'state': 'NSW',
                'postcode': '2000'
            }
        ]
        
        # Act
        result = convert_to_members(sample_data)
        
        # Assert
        assert len(result) == 0