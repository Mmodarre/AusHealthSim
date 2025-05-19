"""
Provider generator for the Health Insurance AU simulation.
"""
import random
import string
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from health_insurance_au.config import STATES
from health_insurance_au.models.models import Provider
from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

# Provider types
PROVIDER_TYPES = [
    'Hospital',
    'General Practitioner',
    'Specialist',
    'Dentist',
    'Optometrist',
    'Physiotherapist',
    'Chiropractor',
    'Psychologist',
    'Podiatrist',
    'Acupuncturist',
    'Naturopath',
    'Massage Therapist'
]

# Hospital names
HOSPITAL_NAMES = [
    'Royal {city} Hospital',
    '{city} Private Hospital',
    '{city} General Hospital',
    'St John\'s Hospital {city}',
    '{city} Memorial Hospital',
    'Northern {city} Hospital',
    'Southern {city} Hospital',
    'Eastern {city} Hospital',
    'Western {city} Hospital',
    '{city} Community Hospital'
]

# Practice names
PRACTICE_NAMES = [
    '{city} {type} Centre',
    '{city} {type} Clinic',
    '{type} Care {city}',
    '{city} {type} Associates',
    'Central {city} {type}',
    '{city} {type} Practice',
    '{type} Specialists of {city}',
    '{city} {type} Group',
    'Premier {type} {city}',
    'Advanced {type} {city}'
]

# Common Australian city names
CITIES = [
    'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Hobart', 'Darwin', 'Canberra',
    'Gold Coast', 'Newcastle', 'Wollongong', 'Geelong', 'Townsville', 'Cairns', 'Toowoomba',
    'Ballarat', 'Bendigo', 'Launceston', 'Mackay', 'Rockhampton', 'Bunbury', 'Bundaberg',
    'Hervey Bay', 'Wagga Wagga', 'Coffs Harbour', 'Gladstone', 'Mildura', 'Shepparton',
    'Port Macquarie', 'Albury', 'Wodonga', 'Warrnambool', 'Orange', 'Geraldton', 'Dubbo'
]

def generate_provider_number() -> str:
    """Generate a random provider number."""
    # Format: 6 digits followed by a letter
    digits = ''.join(random.choices(string.digits, k=6))
    letter = random.choice(string.ascii_uppercase)
    return f"{digits}{letter}"

def generate_providers(count: int = 50, simulation_date: date = None) -> List[Provider]:
    """
    Generate a list of healthcare providers.
    
    Args:
        count: Number of providers to generate
        simulation_date: The date to use for provider generation (default: today)
        
    Returns:
        A list of Provider objects
    """
    providers = []
    
    if simulation_date is None:
        simulation_date = date.today()
    
    # Determine distribution of provider types
    hospital_count = max(5, count // 10)
    specialist_count = max(10, count // 5)
    gp_count = max(10, count // 5)
    other_count = count - hospital_count - specialist_count - gp_count
    
    # Generate hospitals
    for i in range(hospital_count):
        city = random.choice(CITIES)
        state = random.choice(list(STATES.keys()))
        
        # Generate hospital name
        name_template = random.choice(HOSPITAL_NAMES)
        name = name_template.format(city=city)
        
        # Generate a provider number
        provider_number = generate_provider_number()
        
        # Generate address
        address = f"{random.randint(1, 500)} {random.choice(['Hospital', 'Medical Centre', 'Health'])} Road"
        
        # Generate postcode (simplified)
        postcode = f"{random.randint(2000, 7000)}"
        
        # Determine if it's a preferred provider (most hospitals are)
        is_preferred = random.random() < 0.8
        
        # Generate agreement dates if preferred
        agreement_start_date = None
        agreement_end_date = None
        if is_preferred:
            # Start date should be in the past relative to simulation date
            agreement_start_date = simulation_date - timedelta(days=random.randint(30, 730))
            # 80% chance of ongoing agreement
            if random.random() < 0.8:
                # End date should be in the future relative to simulation date
                agreement_end_date = simulation_date + timedelta(days=random.randint(30, 1095))
        
        # Create the provider
        provider = Provider(
            provider_number=provider_number,
            provider_name=name,
            provider_type='Hospital',
            address_line1=address,
            city=city,
            state=state,
            post_code=postcode,
            phone=f"0{random.randint(2, 9)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}",
            email=f"info@{name.lower().replace(' ', '')}.com.au",
            is_preferred_provider=is_preferred,
            agreement_start_date=agreement_start_date,
            agreement_end_date=agreement_end_date
        )
        
        providers.append(provider)
    
    # Generate GPs
    for i in range(gp_count):
        city = random.choice(CITIES)
        state = random.choice(list(STATES.keys()))
        
        # Generate practice name
        name_template = random.choice(PRACTICE_NAMES)
        name = name_template.format(city=city, type='Medical')
        
        # Generate a provider number
        provider_number = generate_provider_number()
        
        # Generate address
        address = f"{random.randint(1, 500)} {random.choice(['Main', 'High', 'Park', 'Church', 'Station'])} Street"
        
        # Generate postcode (simplified)
        postcode = f"{random.randint(2000, 7000)}"
        
        # Determine if it's a preferred provider (some GPs are)
        is_preferred = random.random() < 0.5
        
        # Generate agreement dates if preferred
        agreement_start_date = None
        agreement_end_date = None
        if is_preferred:
            # Start date should be in the past relative to simulation date
            agreement_start_date = simulation_date - timedelta(days=random.randint(30, 730))
            # 60% chance of ongoing agreement
            if random.random() < 0.6:
                # End date should be in the future relative to simulation date
                agreement_end_date = simulation_date + timedelta(days=random.randint(30, 1095))
        
        # Create the provider
        provider = Provider(
            provider_number=provider_number,
            provider_name=name,
            provider_type='General Practitioner',
            address_line1=address,
            city=city,
            state=state,
            post_code=postcode,
            phone=f"0{random.randint(2, 9)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}",
            email=f"info@{name.lower().replace(' ', '')}.com.au",
            is_preferred_provider=is_preferred,
            agreement_start_date=agreement_start_date,
            agreement_end_date=agreement_end_date
        )
        
        providers.append(provider)
    
    # Generate specialists
    for i in range(specialist_count):
        city = random.choice(CITIES)
        state = random.choice(list(STATES.keys()))
        
        # Generate practice name
        specialist_type = random.choice(['Cardiology', 'Orthopedic', 'Dermatology', 'Neurology', 'Oncology', 'Gynecology', 'Urology', 'ENT', 'Ophthalmology'])
        name_template = random.choice(PRACTICE_NAMES)
        name = name_template.format(city=city, type=specialist_type)
        
        # Generate a provider number
        provider_number = generate_provider_number()
        
        # Generate address
        address = f"{random.randint(1, 500)} {random.choice(['Specialist', 'Medical', 'Health', 'Professional'])} Centre"
        
        # Generate postcode (simplified)
        postcode = f"{random.randint(2000, 7000)}"
        
        # Determine if it's a preferred provider (many specialists are)
        is_preferred = random.random() < 0.7
        
        # Generate agreement dates if preferred
        agreement_start_date = None
        agreement_end_date = None
        if is_preferred:
            # Start date should be in the past relative to simulation date
            agreement_start_date = simulation_date - timedelta(days=random.randint(30, 730))
            # 70% chance of ongoing agreement
            if random.random() < 0.7:
                # End date should be in the future relative to simulation date
                agreement_end_date = simulation_date + timedelta(days=random.randint(30, 1095))
        
        # Create the provider
        provider = Provider(
            provider_number=provider_number,
            provider_name=name,
            provider_type=f"Specialist - {specialist_type}",
            address_line1=address,
            city=city,
            state=state,
            post_code=postcode,
            phone=f"0{random.randint(2, 9)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}",
            email=f"info@{name.lower().replace(' ', '')}.com.au",
            is_preferred_provider=is_preferred,
            agreement_start_date=agreement_start_date,
            agreement_end_date=agreement_end_date
        )
        
        providers.append(provider)
    
    # Generate other provider types
    for i in range(other_count):
        city = random.choice(CITIES)
        state = random.choice(list(STATES.keys()))
        
        # Generate practice name
        provider_type = random.choice(PROVIDER_TYPES[3:])  # Skip Hospital, GP, Specialist
        name_template = random.choice(PRACTICE_NAMES)
        name = name_template.format(city=city, type=provider_type)
        
        # Generate a provider number
        provider_number = generate_provider_number()
        
        # Generate address
        address = f"{random.randint(1, 500)} {random.choice(['Main', 'High', 'Park', 'Church', 'Station'])} Street"
        
        # Generate postcode (simplified)
        postcode = f"{random.randint(2000, 7000)}"
        
        # Determine if it's a preferred provider (some are)
        is_preferred = random.random() < 0.4
        
        # Generate agreement dates if preferred
        agreement_start_date = None
        agreement_end_date = None
        if is_preferred:
            # Start date should be in the past relative to simulation date
            agreement_start_date = simulation_date - timedelta(days=random.randint(30, 730))
            # 50% chance of ongoing agreement
            if random.random() < 0.5:
                # End date should be in the future relative to simulation date
                agreement_end_date = simulation_date + timedelta(days=random.randint(30, 1095))
        
        # Create the provider
        provider = Provider(
            provider_number=provider_number,
            provider_name=name,
            provider_type=provider_type,
            address_line1=address,
            city=city,
            state=state,
            post_code=postcode,
            phone=f"0{random.randint(2, 9)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}",
            email=f"info@{name.lower().replace(' ', '')}.com.au",
            is_preferred_provider=is_preferred,
            agreement_start_date=agreement_start_date,
            agreement_end_date=agreement_end_date
        )
        
        providers.append(provider)
    
    logger.info(f"Generated {len(providers)} healthcare providers")
    return providers