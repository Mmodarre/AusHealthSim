"""
Dynamic data generation utilities for the Health Insurance AU simulation.
This module integrates with generate_data.py to create dynamic patient data.
"""
import os
import sys
import json
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

# Import from the data_generation package
from health_insurance_au.utils.data_generation import generate_fixed_records

from health_insurance_au.models.models import Member
from health_insurance_au.utils.logging_config import get_logger
from health_insurance_au.utils.member_tracker import get_unused_members

# Set up logging
logger = get_logger(__name__)

def generate_dynamic_data(count: int = 10) -> List[Dict[str, Any]]:
    """
    Generate dynamic patient data using the generate_data module.
    
    Args:
        count: Number of patients to generate
        
    Returns:
        A list of dictionaries containing the generated data
    """
    try:
        # Generate fixed records using the generate_data module
        fixed_records = generate_fixed_records(count)
        
        # Convert the fixed records to the format expected by the data_loader
        converted_data = []
        
        for patient in fixed_records:
            # Get the most recent seed (current demographic information)
            if not patient.get("seeds"):
                logger.warning(f"No seeds found for patient {patient.get('individualId')}")
                continue
                
            # Sort seeds by end date to get the most recent one
            seeds = sorted(patient["seeds"], key=lambda x: x.get("end", ""), reverse=True)
            current_seed = seeds[0]
            demographics = current_seed.get("demographics", {})
            
            # Extract the data we need
            member_data = {
                "member_id": patient.get("individualId", ""),
                "first_name": demographics.get("first", ""),
                "last_name": demographics.get("last", ""),
                "date_of_birth": patient.get("dateOfBirth", ""),
                "gender": patient.get("gender", ""),
                "address": ", ".join(demographics.get("address", {}).get("line", [])),
                "city": demographics.get("address", {}).get("city", ""),
                "state": demographics.get("address", {}).get("state", ""),
                "postcode": demographics.get("address", {}).get("zip", ""),
                "email": demographics.get("telecom", {}).get("email", ""),
                "mobile_phone": demographics.get("telecom", {}).get("phone", ""),
                "home_phone": "",  # Not provided in the generated data
                "medicare_number": f"{random.randint(1000, 9999)}{random.randint(10000, 99999)}{random.randint(1, 9)}",  # Generate a random Medicare number
                "marital_status": demographics.get("marital_status", "")
            }
            
            # Convert gender to match the expected format (M/F)
            if member_data["gender"] == "male":
                member_data["gender"] = "M"
            elif member_data["gender"] == "female":
                member_data["gender"] = "F"
            
            # Add the converted data
            converted_data.append(member_data)
        
        logger.info(f"Generated {len(converted_data)} records dynamically")
        return converted_data
    except Exception as e:
        logger.error(f"Error generating dynamic data: {e}")
        return []

def convert_to_members(data: List[Dict[str, Any]], count: int = None) -> List[Member]:
    """
    Convert dynamically generated data to Member objects.
    
    Args:
        data: The dynamically generated data as a list of dictionaries
        count: Optional number of members to convert
        
    Returns:
        A list of Member objects
    """
    members = []
    
    # If count is specified, get that many unused members
    if count:
        # Get unused members from the data
        unused_data = get_unused_members(data, count)
        data_to_convert = unused_data
    else:
        data_to_convert = data
    
    for item in data_to_convert:
        try:
            # Parse date of birth
            dob = datetime.strptime(item['date_of_birth'], '%Y-%m-%d').date() if 'date_of_birth' in item else None
            
            # Create a Member object
            member = Member(
                first_name=item.get('first_name', ''),
                last_name=item.get('last_name', ''),
                date_of_birth=dob,
                gender=item.get('gender', ''),
                address_line1=item.get('address', ''),
                city=item.get('city', ''),
                state=item.get('state', ''),
                post_code=str(item.get('postcode', '')),
                member_number=item.get('member_id', ''),
                email=item.get('email', ''),
                mobile_phone=item.get('mobile_phone', ''),
                home_phone=item.get('home_phone', ''),
                medicare_number=item.get('medicare_number', ''),
                # Generate random LHC loading between 0% and 20%
                lhc_loading_percentage=round(random.uniform(0, 20), 2) if random.random() < 0.3 else 0.0,
                # Randomly assign a PHI rebate tier
                phi_rebate_tier=random.choice(['Base', 'Tier1', 'Tier2', 'Tier3']),
                # Generate a join date within the last 5 years
                join_date=date.today() - timedelta(days=random.randint(1, 5*365))
            )
            
            members.append(member)
        except Exception as e:
            logger.error(f"Error converting data to Member: {e}")
            continue
    
    logger.info(f"Converted {len(members)} records to Member objects")
    return members