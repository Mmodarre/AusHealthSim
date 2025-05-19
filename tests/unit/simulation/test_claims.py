"""
Unit tests for the claims module.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timedelta, time
import random

from health_insurance_au.simulation.claims import (
    generate_hospital_claims, generate_general_treatment_claims,
    generate_claim_number
)
from health_insurance_au.models.models import Member, Policy, Provider, Claim

class TestClaimsModule:
    """Tests for the claims module."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_date = date(2022, 4, 15)
        
        # Create test members
        self.test_members = [
            Member(
                first_name='John',
                last_name='Doe',
                date_of_birth=date(1980, 1, 1),
                gender='Male',
                address_line1='123 Main St',
                city='Sydney',
                state='NSW',
                post_code='2000',
                member_number='M10001'
            ),
            Member(
                first_name='Jane',
                last_name='Smith',
                date_of_birth=date(1985, 5, 15),
                gender='Female',
                address_line1='456 High St',
                city='Melbourne',
                state='VIC',
                post_code='3000',
                member_number='M10002'
            )
        ]
        # Add member_id attribute to simulate database ID
        setattr(self.test_members[0], 'member_id', 1)
        setattr(self.test_members[1], 'member_id', 2)
        
        # Create test policies
        self.test_policies = [
            Policy(
                policy_number='POL10001',
                primary_member_id=1,
                plan_id=1,
                coverage_type='Single',
                start_date=date(2022, 1, 1),
                current_premium=200.0,
                last_premium_paid_date=date(2022, 3, 1),
                next_premium_due_date=date(2022, 4, 1)
            ),
            Policy(
                policy_number='POL10002',
                primary_member_id=2,
                plan_id=2,
                coverage_type='Family',
                start_date=date(2022, 2, 1),
                current_premium=150.0,
                last_premium_paid_date=date(2022, 3, 1),
                next_premium_due_date=date(2022, 4, 1)
            )
        ]
        # Add policy_id attribute to simulate database ID
        setattr(self.test_policies[0], 'policy_id', 1)
        setattr(self.test_policies[1], 'policy_id', 2)
        
        # Create test providers
        self.test_providers = [
            Provider(
                provider_number='P10001',
                provider_name='Sydney Medical Center',
                provider_type='Hospital',
                address_line1='789 Health St',
                city='Sydney',
                state='NSW',
                post_code='2000'
            ),
            Provider(
                provider_number='P10002',
                provider_name='Melbourne Dental Clinic',
                provider_type='Dental',
                address_line1='101 Smile Ave',
                city='Melbourne',
                state='VIC',
                post_code='3000'
            )
        ]
        # Add provider_id attribute to simulate database ID
        setattr(self.test_providers[0], 'provider_id', 1)
        setattr(self.test_providers[1], 'provider_id', 2)
    
    def test_generate_claim_number(self):
        """Test generating a claim number."""
        # Act
        claim_number = generate_claim_number(self.test_date)
        
        # Assert
        assert claim_number.startswith('CLM-')
        assert self.test_date.strftime('%Y%m%d') in claim_number
        assert len(claim_number) == 19  # Format: CLM-YYYYMMDD-NNNNN
    
    @patch('health_insurance_au.simulation.claims.random.choices')
    @patch('health_insurance_au.simulation.claims.random.choice')
    @patch('health_insurance_au.utils.datetime_utils.generate_random_datetime')
    @patch('health_insurance_au.simulation.claims.random.uniform')
    @patch('health_insurance_au.simulation.claims.generate_claim_number')
    def test_generate_hospital_claims(self, mock_gen_number, mock_uniform, mock_datetime, mock_choice, mock_choices):
        """Test generating hospital claims."""
        # Arrange
        mock_gen_number.return_value = 'CLM-20220415-00001'
        mock_uniform.return_value = 0.5  # For random calculations
        mock_datetime.side_effect = [
            datetime.combine(self.test_date - timedelta(days=5), time(10, 0, 0)),  # Service date
            datetime.combine(self.test_date - timedelta(days=3), time(14, 0, 0))   # Submission date
        ]
        mock_choice.side_effect = [
            self.test_policies[0],  # Choose first policy
            self.test_providers[0],  # Choose first provider
            {'description': 'Appendectomy', 'number': '30571', 'fee': 445.40},  # MBS item
        ]
        mock_choices.return_value = ['Submitted']  # Status
        
        # Act
        claims = generate_hospital_claims(
            self.test_policies,
            self.test_members,
            self.test_providers,
            count=1,
            simulation_date=self.test_date
        )
        
        # Assert
        assert len(claims) == 1
        claim = claims[0]
        assert claim.claim_number == 'CLM-20220415-00001'
        assert claim.policy_id == 1
        assert claim.member_id == 1
        assert claim.provider_id == 1
        assert claim.claim_type == 'Hospital'
        assert claim.service_description == 'Appendectomy'
        assert claim.mbs_item_number == '30571'
        assert claim.status == 'Submitted'
        
        # Check dates
        assert claim.service_date < claim.submission_date
        assert claim.submission_date <= datetime.combine(self.test_date, datetime.min.time())
    
    @patch('health_insurance_au.simulation.claims.random.choices')
    @patch('health_insurance_au.simulation.claims.random.choice')
    @patch('health_insurance_au.utils.datetime_utils.generate_random_datetime')
    @patch('health_insurance_au.simulation.claims.random.uniform')
    @patch('health_insurance_au.simulation.claims.generate_claim_number')
    def test_generate_general_treatment_claims(self, mock_gen_number, mock_uniform, mock_datetime, mock_choice, mock_choices):
        """Test generating general treatment claims."""
        # Arrange
        mock_gen_number.return_value = 'CLM-20220415-00001'
        mock_uniform.return_value = 0.5  # For random calculations
        mock_datetime.side_effect = [
            datetime.combine(self.test_date - timedelta(days=2), time(10, 0, 0)),  # Service date
            datetime.combine(self.test_date - timedelta(days=1), time(14, 0, 0))   # Submission date
        ]
        mock_choice.side_effect = [
            self.test_policies[0],  # Choose first policy
            'Dental',  # Claim type
            self.test_providers[1],  # Choose second provider (dental)
            {'description': 'Dental Checkup', 'fee': 120.00},  # Service
        ]
        mock_choices.return_value = ['Submitted']  # Status
        
        # Act
        claims = generate_general_treatment_claims(
            self.test_policies,
            self.test_members,
            self.test_providers,
            count=1,
            simulation_date=self.test_date
        )
        
        # Assert
        assert len(claims) == 1
        claim = claims[0]
        assert claim.claim_number == 'CLM-20220415-00001'
        assert claim.policy_id == 1
        assert claim.member_id == 1
        assert claim.provider_id == 2
        assert claim.claim_type == 'Dental'  # Changed from 'General' to match the mock
        assert claim.service_description == 'Dental Checkup'
        assert claim.status == 'Submitted'
        
        # Check dates
        assert claim.service_date < claim.submission_date
        assert claim.submission_date <= datetime.combine(self.test_date, datetime.min.time())
    
    def test_generate_hospital_claims_no_policies(self):
        """Test generating hospital claims with no policies."""
        # Act
        claims = generate_hospital_claims([], self.test_members, self.test_providers, 1, self.test_date)
        
        # Assert
        assert claims == []
    
    def test_generate_hospital_claims_no_members(self):
        """Test generating hospital claims with no members."""
        # Act
        claims = generate_hospital_claims(self.test_policies, [], self.test_providers, 1, self.test_date)
        
        # Assert
        assert claims == []
    
    def test_generate_hospital_claims_no_providers(self):
        """Test generating hospital claims with no providers."""
        # Act
        claims = generate_hospital_claims(self.test_policies, self.test_members, [], 1, self.test_date)
        
        # Assert
        assert claims == []
    
    def test_generate_general_treatment_claims_no_policies(self):
        """Test generating general treatment claims with no policies."""
        # Act
        claims = generate_general_treatment_claims([], self.test_members, self.test_providers, 1, self.test_date)
        
        # Assert
        assert claims == []
    
    def test_generate_general_treatment_claims_no_members(self):
        """Test generating general treatment claims with no members."""
        # Act
        claims = generate_general_treatment_claims(self.test_policies, [], self.test_providers, 1, self.test_date)
        
        # Assert
        assert claims == []
    
    def test_generate_general_treatment_claims_no_providers(self):
        """Test generating general treatment claims with no providers."""
        # Act
        claims = generate_general_treatment_claims(self.test_policies, self.test_members, [], 1, self.test_date)
        
        # Assert
        assert claims == []