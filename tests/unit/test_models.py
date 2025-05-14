"""
Unit tests for the data models.
"""
import json
from datetime import date


def test_member_to_dict(sample_member):
    """Test converting a Member object to a dictionary."""
    member_dict = sample_member.to_dict()
    
    # Verify key fields
    assert member_dict['FirstName'] == "John"
    assert member_dict['LastName'] == "Smith"
    assert member_dict['DateOfBirth'] == date(1980, 1, 15)
    assert member_dict['Gender'] == "Male"
    assert member_dict['Email'] == "john.smith@example.com"
    assert member_dict['MobilePhone'] == "0412345678"
    assert member_dict['MedicareNumber'] == "1234567890"
    assert member_dict['MemberNumber'] == "MEM001"
    assert member_dict['AddressLine1'] == "123 Main St"
    assert member_dict['City'] == "Sydney"
    assert member_dict['State'] == "NSW"
    assert member_dict['PostCode'] == "2000"
    assert member_dict['Country'] == "Australia"


def test_coverage_plan_to_dict(sample_coverage_plan):
    """Test converting a CoveragePlan object to a dictionary."""
    plan_dict = sample_coverage_plan.to_dict()
    
    # Verify key fields
    assert plan_dict['PlanCode'] == "GOLD-HOSP"
    assert plan_dict['PlanName'] == "Gold Hospital Cover"
    assert plan_dict['PlanType'] == "Hospital"
    assert plan_dict['HospitalTier'] == "Gold"
    assert plan_dict['MonthlyPremium'] == 200.00
    assert plan_dict['AnnualPremium'] == 2400.00
    assert plan_dict['EffectiveDate'] == date(2023, 1, 1)
    
    # Test JSON serialization of complex fields
    excess_options = json.loads(plan_dict['ExcessOptions'])
    assert excess_options == [0, 250, 500]
    
    waiting_periods = json.loads(plan_dict['WaitingPeriods'])
    assert waiting_periods['general'] == 2
    assert waiting_periods['pre_existing'] == 12
    assert waiting_periods['pregnancy'] == 12
    
    coverage_details = json.loads(plan_dict['CoverageDetails'])
    assert coverage_details['private_room'] is True
    assert coverage_details['ambulance_cover'] is True


def test_policy_to_dict(sample_policy):
    """Test converting a Policy object to a dictionary."""
    policy_dict = sample_policy.to_dict()
    
    # Verify key fields
    assert policy_dict['PolicyNumber'] == "POL001"
    assert policy_dict['PrimaryMemberID'] == 1
    assert policy_dict['PlanID'] == 1
    assert policy_dict['CoverageType'] == "Single"
    assert policy_dict['StartDate'] == date(2023, 1, 1)
    assert policy_dict['CurrentPremium'] == 200.00
    assert policy_dict['PremiumFrequency'] == "Monthly"
    assert policy_dict['ExcessAmount'] == 250.00
    assert policy_dict['RebatePercentage'] == 25.0
    assert policy_dict['Status'] == "Active"


def test_provider_to_dict(sample_provider):
    """Test converting a Provider object to a dictionary."""
    provider_dict = sample_provider.to_dict()
    
    # Verify key fields
    assert provider_dict['ProviderNumber'] == "PROV001"
    assert provider_dict['ProviderName'] == "Sydney Private Hospital"
    assert provider_dict['ProviderType'] == "Hospital"
    assert provider_dict['AddressLine1'] == "456 Hospital Ave"
    assert provider_dict['City'] == "Sydney"
    assert provider_dict['State'] == "NSW"
    assert provider_dict['PostCode'] == "2000"
    assert provider_dict['Phone'] == "0298765432"
    assert provider_dict['Email'] == "info@sydneyprivate.example.com"
    assert provider_dict['IsPreferredProvider'] is True


def test_claim_to_dict(sample_claim):
    """Test converting a Claim object to a dictionary."""
    claim_dict = sample_claim.to_dict()
    
    # Verify key fields
    assert claim_dict['ClaimNumber'] == "CL-20230515-12345"
    assert claim_dict['PolicyID'] == 1
    assert claim_dict['MemberID'] == 1
    assert claim_dict['ProviderID'] == 1
    assert claim_dict['ServiceDate'] == date(2023, 5, 10)
    assert claim_dict['SubmissionDate'] == date(2023, 5, 15)
    assert claim_dict['ClaimType'] == "Hospital"
    assert claim_dict['ServiceDescription'] == "Appendicectomy"
    assert claim_dict['ChargedAmount'] == 1200.00
    assert claim_dict['MedicareAmount'] == 334.05
    assert claim_dict['InsuranceAmount'] == 615.95
    assert claim_dict['GapAmount'] == 0.00
    assert claim_dict['ExcessApplied'] == 250.00
    assert claim_dict['MBSItemNumber'] == "30390"
    assert claim_dict['Status'] == "Approved"


def test_premium_payment_to_dict(sample_premium_payment):
    """Test converting a PremiumPayment object to a dictionary."""
    payment_dict = sample_premium_payment.to_dict()
    
    # Verify key fields
    assert payment_dict['PolicyID'] == 1
    assert payment_dict['PaymentDate'] == date(2023, 1, 1)
    assert payment_dict['PaymentAmount'] == 200.00
    assert payment_dict['PaymentMethod'] == "Direct Debit"
    assert payment_dict['PeriodStartDate'] == date(2023, 1, 1)
    assert payment_dict['PeriodEndDate'] == date(2023, 1, 31)
    assert payment_dict['PaymentReference'] == "PAY001"
    assert payment_dict['PaymentStatus'] == "Successful"