"""
Main entry point for the Health Insurance AU simulation.
"""
import argparse
import logging
import os
from datetime import datetime, date, timedelta

from health_insurance_au.simulation.simulation import HealthInsuranceSimulation
from health_insurance_au.integration.synthea import SyntheaIntegration
from health_insurance_au.utils.logging_config import configure_logging, get_logger
from health_insurance_au.config import LOG_CONFIG

# Set up logging
logger = get_logger(__name__)

def parse_date(date_str):
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Health Insurance AU Simulation')
    
    # Add logging arguments to the main parser
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
                        default=os.environ.get('HEALTH_INSURANCE_LOG_LEVEL', LOG_CONFIG['default_level']),
                        help='Set the logging level')
    parser.add_argument('--log-file', help='Log to this file (in addition to console)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Daily simulation command
    daily_parser = subparsers.add_parser('daily', help='Run a daily simulation')
    daily_parser.add_argument('--date', type=parse_date, help='Simulation date (YYYY-MM-DD)')
    daily_parser.add_argument('--members', type=int, default=5, help='Number of new members to add')
    daily_parser.add_argument('--plans', type=int, default=0, help='Number of new plans to add')
    daily_parser.add_argument('--policies', type=int, default=3, help='Number of new policies to create')
    daily_parser.add_argument('--hospital-claims', type=int, default=3, help='Number of hospital claims to generate')
    daily_parser.add_argument('--general-claims', type=int, default=10, help='Number of general claims to generate')
    daily_parser.add_argument('--no-members', action='store_true', help='Skip adding new members')
    daily_parser.add_argument('--no-policies', action='store_true', help='Skip creating new policies')
    daily_parser.add_argument('--no-updates', action='store_true', help='Skip updating members')
    daily_parser.add_argument('--no-changes', action='store_true', help='Skip processing policy changes')
    daily_parser.add_argument('--no-hospital-claims', action='store_true', help='Skip generating hospital claims')
    daily_parser.add_argument('--no-general-claims', action='store_true', help='Skip generating general claims')
    daily_parser.add_argument('--no-payments', action='store_true', help='Skip processing premium payments')
    daily_parser.add_argument('--no-claims-processing', action='store_true', help='Skip processing claim assessments')
    
    # Historical simulation command
    historical_parser = subparsers.add_parser('historical', help='Run a historical simulation')
    historical_parser.add_argument('--start-date', type=parse_date, required=True, help='Start date (YYYY-MM-DD)')
    historical_parser.add_argument('--end-date', type=parse_date, help='End date (YYYY-MM-DD)')
    historical_parser.add_argument('--frequency', choices=['daily', 'weekly', 'monthly'], default='daily', help='Simulation frequency')
    
    # Synthea integration command
    synthea_parser = subparsers.add_parser('synthea', help='Integrate with Synthea data')
    synthea_parser.add_argument('--dir', required=True, help='Directory containing Synthea FHIR JSON files')
    synthea_parser.add_argument('--patients', type=int, help='Limit on number of patients to import')
    synthea_parser.add_argument('--encounters', type=int, help='Limit on number of encounters to import')
    synthea_parser.add_argument('--procedures', type=int, help='Limit on number of procedures to import')
    synthea_parser.add_argument('--claims', type=int, help='Limit on number of claims to generate')
    synthea_parser.add_argument('--skip-patients', action='store_true', help='Skip importing patients')
    synthea_parser.add_argument('--skip-encounters', action='store_true', help='Skip importing encounters')
    synthea_parser.add_argument('--skip-procedures', action='store_true', help='Skip importing procedures')
    synthea_parser.add_argument('--skip-linking', action='store_true', help='Skip linking patients to members')
    synthea_parser.add_argument('--skip-claims', action='store_true', help='Skip generating claims from encounters')
    
    args = parser.parse_args()
    
    # Configure logging based on command line arguments
    log_file = args.log_file if args.log_file else None
    if log_file is None and LOG_CONFIG.get('log_file'):
        # Use default log file from config if not specified and config has one
        log_file = os.path.join(LOG_CONFIG['log_dir'], LOG_CONFIG['log_file'])
    
    # Use command line log level if provided, otherwise use environment variable or default
    log_level = args.log_level
    
    # Set environment variable if log level is provided via command line
    if log_level:
        os.environ['HEALTH_INSURANCE_LOG_LEVEL'] = log_level
    
    configure_logging(level=log_level, log_file=log_file)
    
    if args.command == 'daily':
        # Run daily simulation
        simulation = HealthInsuranceSimulation()
        simulation.run_daily_simulation(
            simulation_date=args.date or date.today(),
            add_new_members=not args.no_members,
            new_members_count=args.members,
            add_new_plans=args.plans > 0,
            new_plans_count=args.plans,
            create_new_policies=not args.no_policies,
            new_policies_count=args.policies,
            update_members=not args.no_updates,
            process_policy_changes=not args.no_changes,
            generate_hospital_claims=not args.no_hospital_claims,
            hospital_claims_count=args.hospital_claims,
            generate_general_claims=not args.no_general_claims,
            general_claims_count=args.general_claims,
            process_premium_payments=not args.no_payments,
            process_claims=not args.no_claims_processing
        )
    elif args.command == 'historical':
        # Run historical simulation
        simulation = HealthInsuranceSimulation()
        simulation.run_historical_simulation(
            start_date=args.start_date,
            end_date=args.end_date or date.today(),
            frequency=args.frequency
        )
    elif args.command == 'synthea':
        # Run Synthea integration
        integration = SyntheaIntegration(args.dir)
        
        if not args.skip_patients:
            integration.import_patients(args.patients)
        
        if not args.skip_encounters:
            integration.import_encounters(args.encounters)
        
        if not args.skip_procedures:
            integration.import_procedures(args.procedures)
        
        if not args.skip_linking:
            integration.link_patients_to_members()
        
        if not args.skip_claims:
            integration.generate_claims_from_encounters(args.claims)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()