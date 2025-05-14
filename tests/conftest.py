"""
Pytest configuration file with fixtures for testing.
"""
import os
import sys
import pytest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock pyodbc module
sys.modules['pyodbc'] = MagicMock()

from health_insurance_au.models.models import (
    Member, CoveragePlan, Policy, PolicyMember, Provider, Claim, PremiumPayment
)


@pytest.fixture
def mock_db_connection():
    """Fixture to mock database connection."""
    with patch('pyodbc.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_conn


@pytest.fixture
def sample_member():
    """Fixture to create a sample member."""
    return Member(
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1980, 1, 15),
        gender="Male",
        address_line1="123 Main St",
        city="Sydney",
        state="NSW",
        post_code="2000",
        email="john.smith@example.com",
        mobile_phone="0412345678",
        medicare_number="1234567890",
        member_number="MEM001"
    )


@pytest.fixture
def sample_coverage_plan():
    """Fixture to create a sample coverage plan."""
    return CoveragePlan(
        plan_code="GOLD-HOSP",
        plan_name="Gold Hospital Cover",
        plan_type="Hospital",
        monthly_premium=200.00,
        annual_premium=2400.00,
        effective_date=date(2023, 1, 1),
        hospital_tier="Gold",
        excess_options=[0, 250, 500],
        waiting_periods={
            "general": 2,
            "pre_existing": 12,
            "pregnancy": 12
        },
        coverage_details={
            "private_room": True,
            "ambulance_cover": True
        }
    )


@pytest.fixture
def sample_policy(sample_member, sample_coverage_plan):
    """Fixture to create a sample policy."""
    return Policy(
        policy_number="POL001",
        primary_member_id=1,  # Assuming member ID 1
        plan_id=1,  # Assuming plan ID 1
        coverage_type="Single",
        start_date=date(2023, 1, 1),
        current_premium=200.00,
        premium_frequency="Monthly",
        excess_amount=250.00,
        rebate_percentage=25.0,
        status="Active"
    )


@pytest.fixture
def sample_provider():
    """Fixture to create a sample provider."""
    return Provider(
        provider_number="PROV001",
        provider_name="Sydney Private Hospital",
        provider_type="Hospital",
        address_line1="456 Hospital Ave",
        city="Sydney",
        state="NSW",
        post_code="2000",
        phone="0298765432",
        email="info@sydneyprivate.example.com",
        is_preferred_provider=True
    )


@pytest.fixture
def sample_claim(sample_policy, sample_provider):
    """Fixture to create a sample claim."""
    return Claim(
        claim_number="CL-20230515-12345",
        policy_id=1,  # Assuming policy ID 1
        member_id=1,  # Assuming member ID 1
        provider_id=1,  # Assuming provider ID 1
        service_date=date(2023, 5, 10),
        submission_date=date(2023, 5, 15),
        claim_type="Hospital",
        service_description="Appendicectomy",
        charged_amount=1200.00,
        medicare_amount=334.05,
        insurance_amount=615.95,
        gap_amount=0.00,
        excess_applied=250.00,
        mbs_item_number="30390",
        status="Approved"
    )


@pytest.fixture
def sample_premium_payment(sample_policy):
    """Fixture to create a sample premium payment."""
    return PremiumPayment(
        policy_id=1,  # Assuming policy ID 1
        payment_date=date(2023, 1, 1),
        payment_amount=200.00,
        payment_method="Direct Debit",
        period_start_date=date(2023, 1, 1),
        period_end_date=date(2023, 1, 31),
        payment_reference="PAY001",
        payment_status="Successful"
    )