"""
Add initial data to the Health Insurance AU database using pyodbc.
"""
import argparse
import logging
import sys
import os
import json
from datetime import datetime, date, timedelta
from health_insurance_au.utils.data_loader import load_sample_data, convert_to_members
from health_insurance_au.simulation.coverage_plans import generate_coverage_plans
from health_insurance_au.simulation.providers import generate_providers
from health_insurance_au.utils.db_utils import execute_query, execute_non_query, bulk_insert
from health_insurance_au.config import DB_CONFIG, LOG_CONFIG
from health_insurance_au.utils.logging_config import configure_logging, get_logger

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



# Set up logging
logger = get_logger(__name__)

def add_members(count):
    """Add members to the database."""
    logger.info(f"Adding {count} members...")
    
    # Load sample data
    sample_data = load_sample_data()
    if not sample_data:
        logger.error("Failed to load sample data")
        return 0
    
    # Convert to Member objects
    members = convert_to_members(sample_data, count)
    if not members:
        logger.error("Failed to convert sample data to Member objects")
        return 0
    
    # Prepare data for bulk insert
    members_data = []
    for member in members:
        members_data.append({
            'MemberNumber': member.member_number,
            'Title': member.title,
            'FirstName': member.first_name,
            'LastName': member.last_name,
            'DateOfBirth': member.date_of_birth,
            'Gender': member.gender,
            'Email': member.email,
            'MobilePhone': member.mobile_phone,
            'HomePhone': member.home_phone,
            'AddressLine1': member.address_line1,
            'AddressLine2': member.address_line2,
            'City': member.city,
            'State': member.state,
            'PostCode': member.post_code,
            'Country': member.country,
            'MedicareNumber': member.medicare_number,
            'LHCLoadingPercentage': member.lhc_loading_percentage,
            'PHIRebateTier': member.phi_rebate_tier,
            'JoinDate': member.join_date,
            'IsActive': member.is_active
        })
    
    # Insert into database using bulk insert
    rows_affected = bulk_insert('Insurance.Members', members_data)
    
    logger.info(f"Added {rows_affected} members to the database")
    return rows_affected

def add_coverage_plans(count):
    """Add coverage plans to the database."""
    logger.info(f"Adding {count} coverage plans...")
    
    # Generate coverage plans
    plans = generate_coverage_plans(count)
    if not plans:
        logger.error("Failed to generate coverage plans")
        return 0
    
    # Prepare data for bulk insert
    plans_data = []
    for plan in plans:
        plans_data.append({
            'PlanCode': plan.plan_code,
            'PlanName': plan.plan_name,
            'PlanType': plan.plan_type,
            'HospitalTier': plan.hospital_tier,
            'MonthlyPremium': plan.monthly_premium,
            'AnnualPremium': plan.annual_premium,
            'ExcessOptions': json.dumps(plan.excess_options) if plan.excess_options else None,
            'WaitingPeriods': json.dumps(plan.waiting_periods) if plan.waiting_periods else None,
            'CoverageDetails': json.dumps(plan.coverage_details) if plan.coverage_details else None,
            'IsActive': plan.is_active,
            'EffectiveDate': plan.effective_date,
            'EndDate': plan.end_date
        })
    
    # Insert into database using bulk insert
    rows_affected = bulk_insert('Insurance.CoveragePlans', plans_data)
    
    logger.info(f"Added {rows_affected} coverage plans to the database")
    return rows_affected

def add_providers(count):
    
    """Add providers to the database."""
    logger.info(f"Adding {count} providers...")
    
    # Generate providers
    providers = generate_providers(count)
    if not providers:
        logger.error("Failed to generate providers")
        return 0
    
    # Prepare data for bulk insert
    providers_data = []
    for provider in providers:
        providers_data.append({
            'ProviderNumber': provider.provider_number,
            'ProviderName': provider.provider_name,
            'ProviderType': provider.provider_type,
            'AddressLine1': provider.address_line1,
            'AddressLine2': provider.address_line2,
            'City': provider.city,
            'State': provider.state,
            'PostCode': provider.post_code,
            'Country': provider.country,
            'Phone': provider.phone,
            'Email': provider.email,
            'IsPreferredProvider': provider.is_preferred_provider,
            'AgreementStartDate': provider.agreement_start_date,
            'AgreementEndDate': provider.agreement_end_date,
            'IsActive': provider.is_active
        })
    
    # Insert into database using bulk insert
    rows_affected = bulk_insert('Insurance.Providers', providers_data)
    
    logger.info(f"Added {rows_affected} providers to the database")
    return rows_affected

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Add initial data to the Health Insurance AU database')
    parser.add_argument('--server', help='SQL Server address')
    parser.add_argument('--username', help='SQL Server username')
    parser.add_argument('--password', help='SQL Server password')
    parser.add_argument('--database', help='Database name')
    parser.add_argument('--members', type=int, default=50, help='Number of members to add')
    parser.add_argument('--plans', type=int, default=15, help='Number of coverage plans to add')
    parser.add_argument('--providers', type=int, default=30, help='Number of providers to add')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
                        default=os.environ.get('HEALTH_INSURANCE_LOG_LEVEL', LOG_CONFIG['default_level']),
                        help='Set the logging level')
    parser.add_argument('--log-file', help='Log to this file (in addition to console)')
    parser.add_argument('--env-file', help='Path to environment file with database credentials')
    
    args = parser.parse_args()
    
    # Configure logging based on command line arguments
    log_file = args.log_file if args.log_file else None
    if log_file is None and LOG_CONFIG.get('log_file'):
        # Use default log file from config if not specified and config has one
        log_file = os.path.join(LOG_CONFIG['log_dir'], LOG_CONFIG['log_file'])
    
    configure_logging(level=args.log_level, log_file=log_file)
    
    # Update database configuration from command line if provided
    from health_insurance_au.utils.env_utils import get_db_config
    from health_insurance_au.config import DB_CONFIG
    
    # Get database configuration from environment variables or file
    env_db_config = get_db_config(args.env_file)
    
    # Override DB_CONFIG with environment values and command-line arguments
    if args.server:
        DB_CONFIG['server'] = args.server
    elif env_db_config['server']:
        DB_CONFIG['server'] = env_db_config['server']
        
    if args.username:
        DB_CONFIG['username'] = args.username
    elif env_db_config['username']:
        DB_CONFIG['username'] = env_db_config['username']
        
    if args.password:
        DB_CONFIG['password'] = args.password
    elif env_db_config['password']:
        DB_CONFIG['password'] = env_db_config['password']
        
    if args.database:
        DB_CONFIG['database'] = args.database
    elif env_db_config['database']:
        DB_CONFIG['database'] = env_db_config['database']
    
    # Add members
    #add_members(args.members)
    
    # Add coverage plans
    add_coverage_plans(args.plans)
    
    # Add providers
    add_providers(args.providers)
    
    logger.info("Initial data added successfully")

if __name__ == '__main__':
    main()