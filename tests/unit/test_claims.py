"""
Unit tests for the claims generation module.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
import sys

# Mock pyodbc module
pyodbc = MagicMock()
sys.modules['pyodbc'] = pyodbc

from health_insurance_au.simulation.claims import (
    generate_claim_number, generate_hospital_claims, generate_general_treatment_claims
)
from health_insurance_au.models.models import Policy, Member, Provider


def test_generate_claim_number():
    """Test generating a claim number."""
    with patch('health_insurance_au.simulation.claims.date') as mock_date:
        # Set a fixed date for testing
        mock_date.today.return_value = date(2023, 5, 15)
        # Set a fixed random choice for the numeric part
        with patch('health_insurance_au.simulation.claims.random.choices', return_value=['1', '2', '3', '4', '5']):
            claim_number = generate_claim_number()
            assert claim_number == "CL-20230515-12345"


def test_generate_hospital_claims(sample_policy, sample_member, sample_provider):
    """Test generating hospital claims."""
    # Create test data
    policies = [sample_policy]
    members = [sample_member]
    providers = [sample_provider]
    
    # Set fixed dates for testing
    today = date(2023, 5, 15)
    service_date = date(2023, 5, 10)
    submission_date = date(2023, 5, 12)
    
    with patch('health_insurance_au.simulation.claims.date') as mock_date, \
         patch('health_insurance_au.simulation.claims.random') as mock_random, \
         patch('health_insurance_au.simulation.claims.generate_claim_number', return_value="CL-20230515-12345"):
        
        # Set up mocks
        mock_date.today.return_value = today
        # Need more random.randint values for all the calls in the function
        mock_random.randint.side_effect = [5, 2, 5, 2]  # For dates
        mock_random.choice.side_effect = [
            sample_policy,  # Policy choice
            sample_provider,  # Provider choice
            {'number': '30390', 'description': 'Appendicectomy', 'fee': 445.40},  # MBS item choice
            'Paid'  # Status choice
        ]
        mock_random.random.return_value = 0.1  # Below threshold for excess
        mock_random.uniform.return_value = 2.0  # Markup for charged amount
        mock_random.choices.return_value = ['Paid']  # Status choice
        
        # Generate claims
        claims = generate_hospital_claims(policies, members, providers, count=1)
        
        # Verify a claim was generated
        assert len(claims) == 1
        claim = claims[0]
        
        # Verify claim properties
        assert claim.claim_number == "CL-20230515-12345"
        assert claim.policy_id == 1
        assert claim.member_id == sample_policy.primary_member_id
        assert claim.provider_id == 1
        assert claim.claim_type == "Hospital"
        assert claim.service_description == "Appendicectomy"
        assert claim.mbs_item_number == "30390"
        assert claim.status == "Paid"
        
        # Verify financial calculations - using actual values from the claim
        assert claim.charged_amount == 890.80  # Fee * markup
        assert claim.medicare_amount == 334.05  # 75% of MBS fee
        
        # Verify dates
        assert claim.processed_date is not None
        assert claim.payment_date is not None


def test_generate_hospital_claims_with_excess(sample_policy, sample_member, sample_provider):
    """Test generating hospital claims with excess applied."""
    # Create test data
    policies = [sample_policy]
    members = [sample_member]
    providers = [sample_provider]
    
    # Set fixed dates for testing
    today = date(2023, 5, 15)
    
    with patch('health_insurance_au.simulation.claims.date') as mock_date, \
         patch('health_insurance_au.simulation.claims.random') as mock_random, \
         patch('health_insurance_au.simulation.claims.generate_claim_number', return_value="CL-20230515-12345"):
        
        # Set up mocks
        mock_date.today.return_value = today
        # Add more random.randint values for all calls
        mock_random.randint.side_effect = [5, 2, 5, 2]  # For dates
        mock_random.choice.side_effect = [
            sample_policy,  # Policy choice
            sample_provider,  # Provider choice
            {'number': '30390', 'description': 'Appendicectomy', 'fee': 445.40},  # MBS item choice
            'Paid'  # Status choice
        ]
        mock_random.random.return_value = 0.4  # Above threshold for excess
        mock_random.uniform.return_value = 2.0  # Markup for charged amount
        mock_random.choices.return_value = ['Paid']  # Status choice
        
        # Generate claims
        claims = generate_hospital_claims(policies, members, providers, count=1)
        
        # Verify a claim was generated
        assert len(claims) == 1
        claim = claims[0]
        
        # Get the actual values from the claim
        charged_amount = claim.charged_amount
        medicare_amount = claim.medicare_amount
        excess_applied = claim.excess_applied
        insurance_amount = claim.insurance_amount
        
        # Verify the financial calculations are consistent
        assert insurance_amount == charged_amount - medicare_amount - excess_applied


def test_generate_hospital_claims_rejected(sample_policy, sample_member, sample_provider):
    """Test generating rejected hospital claims."""
    # Create test data
    policies = [sample_policy]
    members = [sample_member]
    providers = [sample_provider]
    
    # Set fixed dates for testing
    today = date(2023, 5, 15)
    
    with patch('health_insurance_au.simulation.claims.date') as mock_date, \
         patch('health_insurance_au.simulation.claims.random') as mock_random, \
         patch('health_insurance_au.simulation.claims.generate_claim_number', return_value="CL-20230515-12345"):
        
        # Set up mocks
        mock_date.today.return_value = today
        mock_random.randint.side_effect = [5, 2, 5]  # For service_date, submission_date, processed_date
        mock_random.choice.side_effect = [
            sample_policy,  # Policy choice
            sample_provider,  # Provider choice
            {'number': '30390', 'description': 'Appendicectomy', 'fee': 445.40},  # MBS item choice
            'Service not covered by policy'  # Rejection reason
        ]
        mock_random.random.return_value = 0.1  # Below threshold for excess
        mock_random.uniform.return_value = 2.0  # Markup for charged amount
        mock_random.choices.return_value = ['Rejected']  # Status choice
        
        # Generate claims
        claims = generate_hospital_claims(policies, members, providers, count=1)
        
        # Verify a claim was generated
        assert len(claims) == 1
        claim = claims[0]
        
        # Verify claim status
        assert claim.status == "Rejected"
        assert claim.rejection_reason == "Service not covered by policy"
        assert claim.processed_date is not None
        assert claim.payment_date is None


def test_generate_general_treatment_claims(sample_policy, sample_member, sample_provider):
    """Test generating general treatment claims."""
    # Create test data
    policies = [sample_policy]
    members = [sample_member]
    
    # Create a general treatment provider
    general_provider = Provider(
        provider_number="PROV002",
        provider_name="Sydney Dental Clinic",
        provider_type="Dental",
        address_line1="789 Dental St",
        city="Sydney",
        state="NSW",
        post_code="2000"
    )
    providers = [general_provider]
    
    # Set fixed dates for testing
    today = date(2023, 5, 15)
    
    with patch('health_insurance_au.simulation.claims.date') as mock_date, \
         patch('health_insurance_au.simulation.claims.random') as mock_random, \
         patch('health_insurance_au.simulation.claims.generate_claim_number', return_value="CL-20230515-12345"):
        
        # Set up mocks
        mock_date.today.return_value = today
        mock_random.randint.side_effect = [5, 2, 3, 2]  # For service_date, submission_date, processed_date, payment_date
        mock_random.choice.side_effect = [
            sample_policy,  # Policy choice
            "Dental",  # Claim type choice
            general_provider,  # Provider choice
            {'description': 'Dental checkup and clean', 'fee': 120.00},  # Service choice
        ]
        mock_random.uniform.return_value = 0.7  # Benefit percentage
        mock_random.choices.return_value = ['Paid']  # Status choice
        
        # Generate claims
        claims = generate_general_treatment_claims(policies, members, providers, count=1)
        
        # Verify a claim was generated
        assert len(claims) == 1
        claim = claims[0]
        
        # Verify claim properties
        assert claim.claim_number == "CL-20230515-12345"
        assert claim.policy_id == 1
        assert claim.member_id == sample_policy.primary_member_id
        assert claim.provider_id == 1
        assert claim.claim_type == "Dental"
        assert claim.service_description == "Dental checkup and clean"
        assert claim.status == "Paid"
        
        # Verify financial calculations
        assert claim.charged_amount == 120.00
        assert claim.medicare_amount == 0.0  # No Medicare for general treatment
        assert claim.excess_applied == 0.0  # No excess for general treatment
        assert claim.insurance_amount == 120.00 * 0.7  # 70% benefit
        assert claim.gap_amount == 120.00 * 0.3  # 30% gap
        
        # Verify dates
        assert claim.processed_date is not None
        assert claim.payment_date is not None


def test_generate_general_treatment_claims_rejected(sample_policy, sample_member, sample_provider):
    """Test generating rejected general treatment claims."""
    # Create test data
    policies = [sample_policy]
    members = [sample_member]
    
    # Create a general treatment provider
    general_provider = Provider(
        provider_number="PROV002",
        provider_name="Sydney Dental Clinic",
        provider_type="Dental",
        address_line1="789 Dental St",
        city="Sydney",
        state="NSW",
        post_code="2000"
    )
    providers = [general_provider]
    
    # Set fixed dates for testing
    today = date(2023, 5, 15)
    
    with patch('health_insurance_au.simulation.claims.date') as mock_date, \
         patch('health_insurance_au.simulation.claims.random') as mock_random, \
         patch('health_insurance_au.simulation.claims.generate_claim_number', return_value="CL-20230515-12345"):
        
        # Set up mocks
        mock_date.today.return_value = today
        mock_random.randint.side_effect = [5, 2, 3]  # For service_date, submission_date, processed_date
        mock_random.choice.side_effect = [
            sample_policy,  # Policy choice
            "Dental",  # Claim type choice
            general_provider,  # Provider choice
            {'description': 'Dental checkup and clean', 'fee': 120.00},  # Service choice
            "Annual limit reached"  # Rejection reason
        ]
        mock_random.uniform.return_value = 0.7  # Benefit percentage
        mock_random.choices.return_value = ['Rejected']  # Status choice
        
        # Generate claims
        claims = generate_general_treatment_claims(policies, members, providers, count=1)
        
        # Verify a claim was generated
        assert len(claims) == 1
        claim = claims[0]
        
        # Verify claim status
        assert claim.status == "Rejected"
        assert claim.rejection_reason == "Annual limit reached"
        assert claim.processed_date is not None
        assert claim.payment_date is None