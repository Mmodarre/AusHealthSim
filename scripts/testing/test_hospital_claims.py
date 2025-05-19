#!/usr/bin/env python3
"""
Simple test script to verify hospital claims date consistency.
"""
from datetime import date
from health_insurance_au.simulation.claims import generate_hospital_claims
from health_insurance_au.models.models import Policy, Member, Provider

def create_test_data():
    """Create test data for claims generation."""
    # Create a test member
    member = Member(
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
    
    # Create a test policy
    policy = Policy(
        policy_number="POL001",
        primary_member_id=1,
        plan_id=1,
        coverage_type="Single",
        start_date=date(2022, 1, 1),
        current_premium=200.00,
        premium_frequency="Monthly",
        excess_amount=250.00,
        rebate_percentage=25.0,
        status="Active"
    )
    
    # Create a test provider
    provider = Provider(
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
    
    return [policy], [member], [provider]

def test_hospital_claims_date():
    """Test date consistency in hospital claims generation."""
    # Create test data
    policies, members, providers = create_test_data()
    
    # Set a specific simulation date
    simulation_date = date(2022, 10, 22)
    
    # Generate claims with the simulation date
    claims = generate_hospital_claims(policies, members, providers, count=2, simulation_date=simulation_date)
    
    print(f"Generated {len(claims)} hospital claims")
    
    # Check date consistency for each claim
    for i, claim in enumerate(claims):
        print(f"\nClaim {i+1}:")
        print(f"  Claim number: {claim.claim_number}")
        print(f"  Service date: {claim.service_date}")
        print(f"  Submission date: {claim.submission_date}")
        print(f"  Status: {claim.status}")
        
        if hasattr(claim, 'processed_date') and claim.processed_date:
            print(f"  Processed date: {claim.processed_date}")
        
        if hasattr(claim, 'payment_date') and claim.payment_date:
            print(f"  Payment date: {claim.payment_date}")
        
        # Check claim number date
        if "20221022" in claim.claim_number:
            print("  ✓ Claim number contains correct date")
        else:
            print("  ✗ Claim number does not contain correct date")
        
        # Check service date
        if claim.service_date.date() <= simulation_date:
            print("  ✓ Service date is before or on simulation date")
        else:
            print("  ✗ Service date is after simulation date")
        
        # Check submission date
        if claim.service_date.date() <= claim.submission_date.date() <= simulation_date:
            print("  ✓ Submission date is between service date and simulation date")
        else:
            print("  ✗ Submission date is not between service date and simulation date")
        
        # For approved/paid claims, check processed and payment dates
        if claim.status in ['Approved', 'Paid'] and claim.processed_date:
            if claim.processed_date.date() <= simulation_date:
                print("  ✓ Processed date is before or on simulation date")
            else:
                print("  ✗ Processed date is after simulation date")
            
            if claim.status == 'Paid' and claim.payment_date:
                if claim.payment_date.date() <= simulation_date:
                    print("  ✓ Payment date is before or on simulation date")
                else:
                    print("  ✗ Payment date is after simulation date")

if __name__ == "__main__":
    test_hospital_claims_date()