"""
Data loading utilities for the Health Insurance AU simulation.
"""
import json
import random
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import os

from health_insurance_au.config import SAMPLE_DATA_PATH
from health_insurance_au.models.models import Member
from health_insurance_au.utils.logging_config import get_logger
from health_insurance_au.utils.member_tracker import get_unused_members

# Set up logging
logger = get_logger(__name__)

def load_sample_data() -> List[Dict[str, Any]]:
    """
    Load sample data from the JSON file.
    
    Returns:
        A list of dictionaries containing the sample data
    """
    try:
        if not os.path.exists(SAMPLE_DATA_PATH):
            logger.error(f"Sample data file not found: {SAMPLE_DATA_PATH}")
            return []
            
        with open(SAMPLE_DATA_PATH, 'r') as f:
            data = json.load(f)
            
        logger.info(f"Loaded {len(data)} records from sample data file")
        return data
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        return []

def convert_to_members(data: List[Dict[str, Any]], count: int = None) -> List[Member]:
    """
    Convert sample data to Member objects.
    
    Args:
        data: The sample data as a list of dictionaries
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