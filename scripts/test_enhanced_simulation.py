#!/usr/bin/env python3
"""
Test script for enhanced simulation features.
"""
import os
import sys
import argparse
from datetime import datetime, date

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from health_insurance_au.data_generation.enhanced_simulation import run_enhanced_simulation
from health_insurance_au.utils.logging_config import configure_logging, get_logger

# Set up logging
configure_logging()
logger = get_logger(__name__)

def main():
    """Main function to test enhanced simulation features."""
    parser = argparse.ArgumentParser(description='Test enhanced simulation features')
    parser.add_argument('--date', help='Simulation date (YYYY-MM-DD)')
    parser.add_argument('--member-profiles', action='store_true', help='Generate member risk profiles')
    parser.add_argument('--policy-attributes', action='store_true', help='Generate policy risk attributes')
    parser.add_argument('--provider-billing', action='store_true', help='Generate provider billing attributes')
    parser.add_argument('--fraud-patterns', action='store_true', help='Apply fraud patterns to claims')
    parser.add_argument('--claim-patterns', action='store_true', help='Generate claim patterns')
    parser.add_argument('--financial-transactions', action='store_true', help='Generate financial transactions')
    parser.add_argument('--actuarial-metrics', action='store_true', help='Generate actuarial metrics')
    args = parser.parse_args()
    
    try:
        # Parse simulation date
        simulation_date = None
        if args.date:
            simulation_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        else:
            simulation_date = date.today()
        
        # Configure enhanced simulation based on command line arguments
        config = {}
        
        # If no specific features are enabled, enable all
        if not any([args.member_profiles, args.policy_attributes, args.provider_billing,
                   args.fraud_patterns, args.claim_patterns, args.financial_transactions,
                   args.actuarial_metrics]):
            config = {
                'generate_member_risk_profiles': True,
                'generate_policy_risk_attributes': True,
                'generate_provider_billing_attributes': True,
                'apply_fraud_patterns': True,
                'generate_claim_patterns': True,
                'generate_financial_transactions': True,
                'generate_actuarial_metrics': True
            }
        else:
            config = {
                'generate_member_risk_profiles': args.member_profiles,
                'generate_policy_risk_attributes': args.policy_attributes,
                'generate_provider_billing_attributes': args.provider_billing,
                'apply_fraud_patterns': args.fraud_patterns,
                'generate_claim_patterns': args.claim_patterns,
                'generate_financial_transactions': args.financial_transactions,
                'generate_actuarial_metrics': args.actuarial_metrics
            }
        
        # Run enhanced simulation
        logger.info(f"Running enhanced simulation for {simulation_date}")
        results = run_enhanced_simulation(simulation_date, config)
        
        # Print summary of results
        print(f"\nEnhanced simulation completed for {simulation_date}:")
        print(f"  Members updated: {results.get('members_updated', 0)}")
        print(f"  Policies updated: {results.get('policies_updated', 0)}")
        print(f"  Providers updated: {results.get('providers_updated', 0)}")
        print(f"  Claims updated: {results.get('claims_updated', 0)}")
        print(f"  Claim patterns generated: {results.get('claim_patterns_generated', 0)}")
        print(f"  Financial transactions generated: {results.get('financial_transactions_generated', 0)}")
        print(f"  Actuarial metrics generated: {results.get('actuarial_metrics_generated', 0)}")
    except Exception as e:
        logger.error(f"Error running enhanced simulation: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()