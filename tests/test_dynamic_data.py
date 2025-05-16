#!/usr/bin/env python3
"""
Test script for dynamic data generation.
This script tests the dynamic_data_generator module.
"""

import sys
import os
from datetime import date, timedelta

from health_insurance_au.utils.dynamic_data_generator import generate_dynamic_data, convert_to_members as convert_dynamic_to_members
from health_insurance_au.simulation.simulation import HealthInsuranceSimulation

def test_dynamic_data_generation():
    """Test dynamic data generation."""
    print("Testing dynamic data generation...")
    
    # Generate dynamic data
    data = generate_dynamic_data(5)
    
    # Print the generated data
    print(f"Generated {len(data)} records:")
    for i, record in enumerate(data):
        print(f"\nRecord {i+1}:")
        print(f"  Member ID: {record.get('member_id')}")
        print(f"  Name: {record.get('first_name')} {record.get('last_name')}")
        print(f"  Gender: {record.get('gender')}")
        print(f"  DOB: {record.get('date_of_birth')}")
        print(f"  Address: {record.get('address')}")
        print(f"  City: {record.get('city')}")
        print(f"  State: {record.get('state')}")
        print(f"  Postcode: {record.get('postcode')}")
        print(f"  Email: {record.get('email')}")
        print(f"  Phone: {record.get('mobile_phone')}")
        print(f"  Medicare: {record.get('medicare_number')}")
    
    # Verify data format constraints
    for record in data:
        # Verify phone number format (should be "04XX XXX XXX")
        phone = record.get('mobile_phone', '')
        assert phone.startswith('04'), f"Phone number should start with '04', got: {phone}"
        assert len(phone) <= 20, f"Phone number too long: {phone}"
        
        # Verify field length constraints
        assert len(record.get('member_id', '')) <= 20, f"Member ID too long: {record.get('member_id')}"
        assert len(record.get('first_name', '')) <= 50, f"First name too long: {record.get('first_name')}"
        assert len(record.get('last_name', '')) <= 50, f"Last name too long: {record.get('last_name')}"
        assert len(record.get('address', '')) <= 100, f"Address too long: {record.get('address')}"
        assert len(record.get('city', '')) <= 50, f"City too long: {record.get('city')}"
        assert len(record.get('state', '')) <= 3, f"State too long: {record.get('state')}"
        assert len(record.get('postcode', '')) <= 10, f"Postcode too long: {record.get('postcode')}"
        assert len(record.get('email', '')) <= 100, f"Email too long: {record.get('email')}"
        assert len(record.get('medicare_number', '')) <= 15, f"Medicare number too long: {record.get('medicare_number')}"
    
    # Convert to Member objects
    members = convert_dynamic_to_members(data)
    
    # Print the converted members
    print(f"\nConverted to {len(members)} Member objects:")
    for i, member in enumerate(members):
        print(f"\nMember {i+1}:")
        print(f"  Member Number: {member.member_number}")
        print(f"  Name: {member.first_name} {member.last_name}")
        print(f"  Gender: {member.gender}")
        print(f"  DOB: {member.date_of_birth}")
        print(f"  Address: {member.address_line1}")
        print(f"  City: {member.city}")
        print(f"  State: {member.state}")
        print(f"  Post Code: {member.post_code}")
        print(f"  Email: {member.email}")
        print(f"  Mobile: {member.mobile_phone}")
        print(f"  Medicare: {member.medicare_number}")
    
    # Verify member object phone number format
    for member in members:
        phone = member.mobile_phone
        assert phone.startswith('04'), f"Phone number should start with '04', got: {phone}"
        assert len(phone) <= 20, f"Phone number too long: {phone}"
    
    return len(data) > 0 and len(members) > 0

def test_simulation_with_dynamic_data():
    """Test the simulation with dynamic data."""
    print("\nTesting simulation with dynamic data...")
    
    # Create a simulation instance
    simulation = HealthInsuranceSimulation()
    
    # Run a single day simulation with dynamic data
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    simulation.run_daily_simulation(
        simulation_date=yesterday,
        add_new_members=True,
        new_members_count=3,
        use_dynamic_data=True,
        add_new_plans=False,
        add_new_providers=False,
        create_new_policies=False,
        update_members=False,
        update_providers=False,
        end_provider_agreements=False,
        process_policy_changes=False,
        generate_hospital_claims=False,
        generate_general_claims=False,
        process_premium_payments=False,
        process_claims=False
    )
    
    print("Simulation with dynamic data completed successfully!")
    return True

if __name__ == "__main__":
    success = test_dynamic_data_generation()
    if success:
        print("\nDynamic data generation test passed!")
    else:
        print("\nDynamic data generation test failed!")
        sys.exit(1)
    
    try:
        success = test_simulation_with_dynamic_data()
        if success:
            print("\nSimulation with dynamic data test passed!")
        else:
            print("\nSimulation with dynamic data test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\nSimulation with dynamic data test failed with error: {e}")
        sys.exit(1)
    
    print("\nAll tests passed successfully!")