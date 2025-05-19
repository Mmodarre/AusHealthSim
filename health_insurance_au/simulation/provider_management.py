"""
Provider management utilities for the Health Insurance AU simulation.
"""
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from health_insurance_au.models.models import Provider
from health_insurance_au.simulation.providers import generate_providers, CITIES, STATES
from health_insurance_au.utils.logging_config import get_logger
from health_insurance_au.utils.datetime_utils import generate_random_datetime
from health_insurance_au.utils.db_utils import execute_query, execute_non_query

# Set up logging
logger = get_logger(__name__)

def end_provider_agreements(percentage: float = 5.0, simulation_date: Optional[date] = None):
    """
    End agreements for a percentage of providers in the database.
    
    Args:
        percentage: Percentage of providers to end agreements for
        simulation_date: The date to use for LastModified
    """
    logger.info(f"Ending agreements for approximately {percentage}% of providers...")
    
    if simulation_date is None:
        simulation_date = date.today()
    
    # Get active preferred providers with no end date from database
    providers_data = execute_query("""
        SELECT * FROM Insurance.Providers 
        WHERE IsActive = 1 AND IsPreferredProvider = 1 
        AND AgreementStartDate IS NOT NULL AND AgreementEndDate IS NULL
    """)
    
    if not providers_data:
        logger.warning("No active preferred providers available to end agreements")
        return
    
    # Calculate number of providers to update
    count = max(1, int(len(providers_data) * percentage / 100))
    
    # Select random providers to update
    providers_to_update = random.sample(providers_data, min(count, len(providers_data)))
    
    updated_count = 0
    for provider in providers_to_update:
        # Set end date to a random date in the future relative to simulation date
        end_date = simulation_date + timedelta(days=random.randint(30, 90))
        
        # Update the database
        try:
            query = """
            UPDATE Insurance.Providers
            SET AgreementEndDate = ?, LastModified = ?
            WHERE ProviderNumber = ?
            """
            execute_non_query(query, (end_date, simulation_date, provider['ProviderNumber']), simulation_date)
            updated_count += 1
        except Exception as e:
            logger.error(f"Error updating provider agreement {provider['ProviderNumber']}: {e}")
    
    logger.info(f"Ended agreements for {updated_count} providers")

def update_provider_details(percentage: float = 10.0, simulation_date: Optional[date] = None):
    """
    Update details for a percentage of providers in the database.
    
    Args:
        percentage: Percentage of providers to update
        simulation_date: The date to use for LastModified
    """
    logger.info(f"Updating approximately {percentage}% of providers...")
    
    if simulation_date is None:
        simulation_date = date.today()
    
    # Get providers from database
    providers_data = execute_query("SELECT * FROM Insurance.Providers WHERE IsActive = 1")
    
    if not providers_data:
        logger.warning("No providers available to update")
        return
    
    # Calculate number of providers to update
    count = max(1, int(len(providers_data) * percentage / 100))
    
    # Select random providers to update
    providers_to_update = random.sample(providers_data, min(count, len(providers_data)))
    
    updated_count = 0
    for provider in providers_to_update:
        # Randomly select what to update
        update_type = random.choice(['contact', 'address', 'both'])
        
        # Initialize update fields
        phone = provider['Phone']
        email = provider['Email']
        address_line1 = provider['AddressLine1']
        city = provider['City']
        state = provider['State']
        post_code = provider['PostCode']
        is_preferred_provider = provider['IsPreferredProvider']
        agreement_start_date = provider['AgreementStartDate']
        agreement_end_date = provider['AgreementEndDate']
        
        if update_type in ['contact', 'both']:
            # Update contact information
            phone = f"0{random.randint(2, 9)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"
            email = f"info@{provider['ProviderName'].lower().replace(' ', '')}.com.au"
        
        if update_type in ['address', 'both']:
            # Update address (50% chance)
            if random.random() < 0.5:
                address_line1 = f"{random.randint(1, 500)} {random.choice(['Main', 'High', 'Park', 'Church', 'Station'])} Street"
            
            # Update city and state (25% chance)
            if random.random() < 0.25:
                city = random.choice(CITIES)
                state = random.choice(list(STATES.keys()))
                post_code = f"{random.randint(2000, 7000)}"
        
        # Small chance (5%) of changing preferred provider status
        if random.random() < 0.05:
            is_preferred_provider = not is_preferred_provider
            
            # If becoming preferred, add agreement dates
            if is_preferred_provider:
                agreement_start_date = simulation_date
                # 70% chance of having an end date
                if random.random() < 0.7:
                    agreement_end_date = simulation_date + timedelta(days=random.randint(365, 1095))
            else:
                agreement_start_date = None
                agreement_end_date = None
        
        # Update the database
        try:
            query = """
            UPDATE Insurance.Providers
            SET Phone = ?, Email = ?, AddressLine1 = ?, City = ?, State = ?, PostCode = ?,
                IsPreferredProvider = ?, AgreementStartDate = ?, AgreementEndDate = ?, LastModified = ?
            WHERE ProviderNumber = ?
            """
            execute_non_query(query, (
                phone, 
                email, 
                address_line1, 
                city, 
                state, 
                post_code, 
                1 if is_preferred_provider else 0, 
                agreement_start_date, 
                agreement_end_date,
                simulation_date,
                provider['ProviderNumber']
            ), simulation_date)
            updated_count += 1
        except Exception as e:
            logger.error(f"Error updating provider {provider['ProviderNumber']}: {e}")
    
    logger.info(f"Updated details for {updated_count} providers")