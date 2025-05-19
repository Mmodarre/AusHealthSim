#!/usr/bin/env python3
"""
End-to-end test script for date consistency in the insurance simulation.

This script runs a simulation for a specific date and then queries the database
to verify that all dates in the generated data are consistent with the simulation date.

Usage:
    python test_date_consistency_e2e.py --date YYYY-MM-DD

Example:
    python test_date_consistency_e2e.py --date 2022-10-22
"""

import argparse
import logging
import sys
import os
from datetime import datetime, date, timedelta
from typing import Dict, Any, List

# Add parent directory to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from health_insurance_au.simulation.simulation import HealthInsuranceSimulation
    from health_insurance_au.utils.db_utils import execute_query
    from health_insurance_au.utils.logging_config import configure_logging, get_logger
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

# Set up logging
logger = get_logger(__name__)

def parse_date(date_str):
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

def check_claim_dates(simulation_date: date) -> bool:
    """
    Check that all claim dates are consistent with the simulation date.
    
    Args:
        simulation_date: The simulation date to check against
        
    Returns:
        True if all dates are consistent, False otherwise
    """
    # Query claims created on the simulation date
    claims = execute_query(f"""
        SELECT ClaimNumber, ServiceDate, SubmissionDate, ProcessedDate, PaymentDate, LastModified
        FROM Insurance.Claims
        WHERE CONVERT(date, LastModified) = '{simulation_date.strftime('%Y-%m-%d')}'
    """)
    
    if not claims:
        logger.warning("No claims found for the simulation date")
        return True
    
    logger.info(f"Found {len(claims)} claims to check")
    
    all_consistent = True
    for claim in claims:
        claim_number = claim['ClaimNumber']
        
        # Check claim number format
        date_part = simulation_date.strftime('%Y%m%d')
        if date_part not in claim_number:
            logger.error(f"Claim {claim_number} does not contain simulation date {date_part}")
            all_consistent = False
        
        # Check service date
        service_date = claim['ServiceDate']
        if service_date and (isinstance(service_date, datetime) and service_date.date() > simulation_date or
                           isinstance(service_date, date) and service_date > simulation_date):
            service_date_str = service_date.date() if isinstance(service_date, datetime) else service_date
            logger.error(f"Claim {claim_number} has service date {service_date_str} after simulation date {simulation_date}")
            all_consistent = False
        
        # Check submission date
        submission_date = claim['SubmissionDate']
        if submission_date and (isinstance(submission_date, datetime) and submission_date.date() > simulation_date or
                              isinstance(submission_date, date) and submission_date > simulation_date):
            submission_date_str = submission_date.date() if isinstance(submission_date, datetime) else submission_date
            logger.error(f"Claim {claim_number} has submission date {submission_date_str} after simulation date {simulation_date}")
            all_consistent = False
        
        # Check processed date
        processed_date = claim['ProcessedDate']
        if processed_date and (isinstance(processed_date, datetime) and processed_date.date() > simulation_date or
                             isinstance(processed_date, date) and processed_date > simulation_date):
            processed_date_str = processed_date.date() if isinstance(processed_date, datetime) else processed_date
            logger.error(f"Claim {claim_number} has processed date {processed_date_str} after simulation date {simulation_date}")
            all_consistent = False
        
        # Check payment date
        payment_date = claim['PaymentDate']
        if payment_date and (isinstance(payment_date, datetime) and payment_date.date() > simulation_date or
                           isinstance(payment_date, date) and payment_date > simulation_date):
            payment_date_str = payment_date.date() if isinstance(payment_date, datetime) else payment_date
            logger.error(f"Claim {claim_number} has payment date {payment_date_str} after simulation date {simulation_date}")
            all_consistent = False
    
    return all_consistent

def check_provider_dates(simulation_date: date) -> bool:
    """
    Check that all provider dates are consistent with the simulation date.
    
    Args:
        simulation_date: The simulation date to check against
        
    Returns:
        True if all dates are consistent, False otherwise
    """
    # Query providers created or updated on the simulation date
    providers = execute_query(f"""
        SELECT ProviderNumber, AgreementStartDate, AgreementEndDate, LastModified
        FROM Insurance.Providers
        WHERE CONVERT(date, LastModified) = '{simulation_date.strftime('%Y-%m-%d')}'
    """)
    
    if not providers:
        logger.warning("No providers found for the simulation date")
        return True
    
    logger.info(f"Found {len(providers)} providers to check")
    
    all_consistent = True
    for provider in providers:
        provider_number = provider['ProviderNumber']
        
        # Check agreement start date
        start_date = provider['AgreementStartDate']
        if start_date and (isinstance(start_date, datetime) and start_date.date() > simulation_date or
                         isinstance(start_date, date) and start_date > simulation_date):
            start_date_str = start_date.date() if isinstance(start_date, datetime) else start_date
            logger.error(f"Provider {provider_number} has agreement start date {start_date_str} after simulation date {simulation_date}")
            all_consistent = False
    
    return all_consistent

def check_policy_dates(simulation_date: date) -> bool:
    """
    Check that all policy dates are consistent with the simulation date.
    
    Args:
        simulation_date: The simulation date to check against
        
    Returns:
        True if all dates are consistent, False otherwise
    """
    # Query policies created or updated on the simulation date
    policies = execute_query(f"""
        SELECT PolicyNumber, StartDate, LastPremiumPaidDate, LastModified
        FROM Insurance.Policies
        WHERE CONVERT(date, LastModified) = '{simulation_date.strftime('%Y-%m-%d')}'
    """)
    
    if not policies:
        logger.warning("No policies found for the simulation date")
        return True
    
    logger.info(f"Found {len(policies)} policies to check")
    
    all_consistent = True
    for policy in policies:
        policy_number = policy['PolicyNumber']
        
        # Check start date
        start_date = policy['StartDate']
        if start_date and (isinstance(start_date, datetime) and start_date.date() > simulation_date or
                         isinstance(start_date, date) and start_date > simulation_date):
            start_date_str = start_date.date() if isinstance(start_date, datetime) else start_date
            logger.error(f"Policy {policy_number} has start date {start_date_str} after simulation date {simulation_date}")
            all_consistent = False
        
        # Check last premium paid date
        paid_date = policy['LastPremiumPaidDate']
        if paid_date and (isinstance(paid_date, datetime) and paid_date.date() > simulation_date or
                        isinstance(paid_date, date) and paid_date > simulation_date):
            paid_date_str = paid_date.date() if isinstance(paid_date, datetime) else paid_date
            logger.error(f"Policy {policy_number} has last premium paid date {paid_date_str} after simulation date {simulation_date}")
            all_consistent = False
        
        # Note: NextPremiumDueDate is allowed to be in the future
    
    return all_consistent

def check_premium_payment_dates(simulation_date: date) -> bool:
    """
    Check that all premium payment dates are consistent with the simulation date.
    
    Args:
        simulation_date: The simulation date to check against
        
    Returns:
        True if all dates are consistent, False otherwise
    """
    # Query premium payments created on the simulation date
    payments = execute_query(f"""
        SELECT PaymentReference, PaymentDate, LastModified
        FROM Insurance.PremiumPayments
        WHERE CONVERT(date, LastModified) = '{simulation_date.strftime('%Y-%m-%d')}'
    """)
    
    if not payments:
        logger.warning("No premium payments found for the simulation date")
        return True
    
    logger.info(f"Found {len(payments)} premium payments to check")
    
    all_consistent = True
    for payment in payments:
        payment_ref = payment['PaymentReference']
        
        # Check payment reference format
        date_part = simulation_date.strftime('%Y%m%d')
        if date_part not in payment_ref:
            logger.error(f"Payment {payment_ref} does not contain simulation date {date_part}")
            all_consistent = False
        
        # Check payment date
        payment_date = payment['PaymentDate']
        if payment_date and (isinstance(payment_date, datetime) and payment_date.date() != simulation_date or
                           isinstance(payment_date, date) and payment_date != simulation_date):
            payment_date_str = payment_date.date() if isinstance(payment_date, datetime) else payment_date
            logger.error(f"Payment {payment_ref} has payment date {payment_date_str} different from simulation date {simulation_date}")
            all_consistent = False
    
    return all_consistent

def run_test(simulation_date: date) -> bool:
    """
    Run a simulation for the specified date and verify date consistency.
    
    Args:
        simulation_date: The date to run the simulation for
        
    Returns:
        True if all tests pass, False otherwise
    """
    logger.info(f"Running simulation for date: {simulation_date}")
    
    # Initialize the simulation
    simulation = HealthInsuranceSimulation()
    
    # Run a daily simulation
    simulation.run_daily_simulation(
        simulation_date=simulation_date,
        new_members_count=5,
        add_new_plans=True,
        new_plans_count=1,
        new_providers_count=3,
        new_policies_count=3,
        hospital_claims_count=5,
        general_claims_count=10
    )
    
    logger.info("Simulation completed. Checking date consistency...")
    
    # Check dates in different entities
    claim_dates_ok = check_claim_dates(simulation_date)
    provider_dates_ok = check_provider_dates(simulation_date)
    policy_dates_ok = check_policy_dates(simulation_date)
    payment_dates_ok = check_premium_payment_dates(simulation_date)
    
    # Overall result
    all_tests_pass = claim_dates_ok and provider_dates_ok and policy_dates_ok and payment_dates_ok
    
    if all_tests_pass:
        logger.info("All date consistency checks passed!")
    else:
        logger.error("Some date consistency checks failed!")
    
    return all_tests_pass

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Test date consistency in insurance simulation')
    parser.add_argument('--date', type=parse_date, required=True, help='Simulation date (YYYY-MM-DD)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Set the logging level')
    
    args = parser.parse_args()
    
    # Configure logging
    configure_logging(level=args.log_level)
    
    # Run the test
    success = run_test(args.date)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()