#!/usr/bin/env python3
"""
Realistic Health Insurance Simulation Script

This script runs a simulation between a start and end date, generating realistic
health insurance data with members joining, leaving, making claims, etc.

The script only requires the number of new members per day and automatically
adjusts other factors to create realistic simulation data.
"""

import argparse
import logging
import random
from datetime import datetime, date, timedelta, time
from typing import Dict, Any

from health_insurance_au.simulation.simulation import HealthInsuranceSimulation
from health_insurance_au.utils.logging_config import configure_logging, get_logger

# Set up logging
logger = get_logger(__name__)

def parse_date(date_str):
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

def generate_random_datetime(simulation_date):
    """Generate a random datetime within the given date."""
    random_hour = random.randint(8, 17)  # Business hours (8 AM to 5 PM)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    return datetime.combine(simulation_date, time(random_hour, random_minute, random_second))

def calculate_daily_parameters(base_members_count: int) -> Dict[str, Any]:
    """
    Calculate realistic parameters for daily simulation based on the number of members.
    
    Args:
        base_members_count: Base number of new members per day
    
    Returns:
        Dictionary of parameters for the daily simulation
    """
    # Add some randomness to the base count (±20%)
    members_count = max(1, int(base_members_count * random.uniform(0.8, 1.2)))
    
    # Calculate other parameters based on the members count
    # These ratios are designed to create realistic relationships between parameters
    params = {
        "add_new_members": True,
        "new_members_count": members_count,
        
        # New plans are rare (about 1% chance per day)
        "add_new_plans": random.random() < 0.01,
        "new_plans_count": 1 if random.random() < 0.01 else 0,
        
        # New policies are roughly 60-80% of new members
        "create_new_policies": True,
        "new_policies_count": max(1, int(members_count * random.uniform(0.6, 0.8))),
        
        # About 1-3% of existing members update their information each day
        "update_members": True,
        "member_update_percentage": random.uniform(5.0, 7.0),
        
        # About 0.5-1.5% of policies change each day
        "process_policy_changes": True,
        "policy_change_percentage": random.uniform(0.5, 1.5),
        
        # Hospital claims are roughly 10-20% of the member count
        "generate_hospital_claims": True,
        "hospital_claims_count": max(1, int(members_count * random.uniform(0.1, 0.2))),
        
        # General claims are roughly 30-50% of the member count
        "generate_general_claims": True,
        "general_claims_count": max(1, int(members_count * random.uniform(0.3, 0.5))),
        
        # Always process premium payments
        "process_premium_payments": True,
        
        # Always process claims, with 75-95% of claims being processed
        "process_claims": True,
        "claim_process_percentage": random.uniform(75.0, 95.0)
    }
    
    return params

def run_realistic_simulation(start_date: date, end_date: date, base_members_per_day: int, log_level: str = 'INFO'):
    """
    Run a realistic health insurance simulation between the specified dates.
    
    Args:
        start_date: Start date for the simulation
        end_date: End date for the simulation
        base_members_per_day: Base number of new members per day
        log_level: Logging level
    """
    # Configure logging
    configure_logging(level=log_level)
    
    logger.info(f"Starting realistic simulation from {start_date} to {end_date}")
    logger.info(f"Base members per day: {base_members_per_day}")
    
    # Initialize the simulation
    simulation = HealthInsuranceSimulation()
    
    # Run the simulation for each day
    current_date = start_date
    day_count = 0
    
    while current_date <= end_date:
        day_count += 1
        logger.info(f"Simulating day {day_count}: {current_date}")
        
        # Calculate parameters for this day
        params = calculate_daily_parameters(base_members_per_day)
        
        # Add some weekly and monthly patterns
        # Fewer members join on weekends
        if current_date.weekday() >= 5:  # Saturday or Sunday
            params["new_members_count"] = max(1, int(params["new_members_count"] * 0.6))
            params["new_policies_count"] = max(1, int(params["new_policies_count"] * 0.6))
        
        # More claims at the beginning and end of the month
        day_of_month = current_date.day
        if day_of_month <= 5 or day_of_month >= 25:
            params["hospital_claims_count"] = int(params["hospital_claims_count"] * 1.2)
            params["general_claims_count"] = int(params["general_claims_count"] * 1.2)
        
        # Run the daily simulation with the calculated parameters
        simulation.run_daily_simulation(
            simulation_date=current_date,
            **params
        )
        
        # Move to the next day
        current_date += timedelta(days=1)
    
    logger.info(f"Simulation completed. Simulated {day_count} days from {start_date} to {end_date}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Realistic Health Insurance Simulation')
    
    parser.add_argument('--start-date', type=parse_date, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=parse_date, required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--members-per-day', type=int, default=10, help='Base number of new members per day')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Set the logging level')
    parser.add_argument('--reset-members', action='store_true', help='Reset the list of used member IDs before running')
    
    args = parser.parse_args()
    
    # Validate dates
    if args.start_date > args.end_date:
        parser.error("End date must be after start date")
    
    # Reset the used members list if requested
    if args.reset_members:
        from health_insurance_au.utils.member_tracker import reset_used_members
        reset_used_members()
        logger.info("Reset the list of used member IDs")
    
    # Run the simulation
    run_realistic_simulation(
        start_date=args.start_date,
        end_date=args.end_date,
        base_members_per_day=args.members_per_day,
        log_level=args.log_level
    )

if __name__ == '__main__':
    main()