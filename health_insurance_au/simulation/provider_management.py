"""
Provider management utilities for the Health Insurance AU simulation.
"""
import random
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from health_insurance_au.models.models import Provider
from health_insurance_au.simulation.providers import generate_providers, CITIES, STATES
from health_insurance_au.utils.logging_config import get_logger
from health_insurance_au.utils.datetime_utils import generate_random_datetime

# Set up logging
logger = get_logger(__name__)

def end_provider_agreements(providers: List[Provider], percentage: float = 5.0) -> List[Provider]:
    """
    End agreements for a percentage of providers.
    
    Args:
        providers: List of providers
        percentage: Percentage of providers to end agreements for
        
    Returns:
        List of providers with ended agreements
    """
    # Filter for active preferred providers with no end date
    active_preferred_providers = [
        p for p in providers 
        if p.is_preferred_provider and p.is_active and p.agreement_start_date and not p.agreement_end_date
    ]
    
    if not active_preferred_providers:
        logger.warning("No active preferred providers available to end agreements")
        return []
    
    # Calculate number of providers to update
    count = max(1, int(len(active_preferred_providers) * percentage / 100))
    
    # Select random providers to update
    providers_to_update = random.sample(active_preferred_providers, min(count, len(active_preferred_providers)))
    
    # End agreements
    for provider in providers_to_update:
        # Set end date to a random date in the next 30-90 days
        end_date = date.today() + timedelta(days=random.randint(30, 90))
        provider.agreement_end_date = end_date
        
    logger.info(f"Ended agreements for {len(providers_to_update)} providers")
    return providers_to_update

def update_provider_details(providers: List[Provider], percentage: float = 10.0) -> List[Provider]:
    """
    Update details for a percentage of providers.
    
    Args:
        providers: List of providers
        percentage: Percentage of providers to update
        
    Returns:
        List of updated providers
    """
    if not providers:
        logger.warning("No providers available to update")
        return []
    
    # Calculate number of providers to update
    count = max(1, int(len(providers) * percentage / 100))
    
    # Select random providers to update
    providers_to_update = random.sample(providers, min(count, len(providers)))
    
    # Update provider details
    for provider in providers_to_update:
        # Randomly select what to update
        update_type = random.choice(['contact', 'address', 'both'])
        
        if update_type in ['contact', 'both']:
            # Update contact information
            provider.phone = f"0{random.randint(2, 9)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"
            provider.email = f"info@{provider.provider_name.lower().replace(' ', '')}.com.au"
        
        if update_type in ['address', 'both']:
            # Update address (50% chance)
            if random.random() < 0.5:
                provider.address_line1 = f"{random.randint(1, 500)} {random.choice(['Main', 'High', 'Park', 'Church', 'Station'])} Street"
            
            # Update city and state (25% chance)
            if random.random() < 0.25:
                provider.city = random.choice(CITIES)
                provider.state = random.choice(list(STATES.keys()))
                provider.post_code = f"{random.randint(2000, 7000)}"
        
        # Small chance (5%) of changing preferred provider status
        if random.random() < 0.05:
            provider.is_preferred_provider = not provider.is_preferred_provider
            
            # If becoming preferred, add agreement dates
            if provider.is_preferred_provider:
                provider.agreement_start_date = date.today()
                # 70% chance of having an end date
                if random.random() < 0.7:
                    provider.agreement_end_date = date.today() + timedelta(days=random.randint(365, 1095))
            else:
                provider.agreement_start_date = None
                provider.agreement_end_date = None
    
    logger.info(f"Updated details for {len(providers_to_update)} providers")
    return providers_to_update