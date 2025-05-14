"""
Enable Change Data Capture (CDC) on the Health Insurance AU database using pyodbc.
"""
import argparse
import logging
import sys
import os
from health_insurance_au.utils.db_utils import execute_non_query, execute_query
from health_insurance_au.config import DB_CONFIG, LOG_CONFIG
from health_insurance_au.utils.logging_config import configure_logging, get_logger
from health_insurance_au.utils.env_utils import get_db_config

# Set up logging
logger = get_logger(__name__)

def enable_cdc_on_database(database_name):
    """Enable CDC on the database."""
    logger.info(f"Enabling CDC on database {database_name}...")
    
    # Check if SQL Server Agent is running (required for CDC)
    agent_check = execute_query("SELECT dbo.fn_hadr_is_primary_replica('master') as is_primary")
    logger.info(f"Agent check result: {agent_check}")
    
    # Enable CDC on the database
    sql = f"""
    IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = '{database_name}' AND is_cdc_enabled = 1)
    BEGIN
        EXEC sys.sp_cdc_enable_db;
        PRINT 'CDC enabled on database {database_name}';
    END
    ELSE
    BEGIN
        PRINT 'CDC already enabled on database {database_name}';
    END
    """
    
    try:
        result = execute_non_query(sql)
        logger.info(f"CDC enable result: {result}")
        logger.info(f"CDC enabled on database {database_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to enable CDC on database {database_name}: {e}")
        return False

def enable_cdc_on_table(schema_name, table_name, role_name='cdc_admin'):
    """Enable CDC on a specific table."""
    logger.info(f"Enabling CDC on table {schema_name}.{table_name}...")
    
    # Enable CDC on the table
    sql = f"""
    IF NOT EXISTS (
        SELECT 1 FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE s.name = '{schema_name}' AND t.name = '{table_name}' AND t.is_tracked_by_cdc = 1
    )
    BEGIN
        EXEC sys.sp_cdc_enable_table
            @source_schema = '{schema_name}',
            @source_name = '{table_name}',
            @role_name = '{role_name}',
            @supports_net_changes = 1;
        PRINT 'CDC enabled on table {schema_name}.{table_name}';
    END
    ELSE
    BEGIN
        PRINT 'CDC already enabled on table {schema_name}.{table_name}';
    END
    """
    
    try:
        result = execute_non_query(sql)
        logger.info(f"CDC enable table result: {result}")
        logger.info(f"CDC enabled on table {schema_name}.{table_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to enable CDC on table {schema_name}.{table_name}: {e}")
        return False

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Enable CDC on the Health Insurance AU database')
    parser.add_argument('--database', help='Database name')
    parser.add_argument('--server', help='SQL Server address')
    parser.add_argument('--username', help='SQL Server username')
    parser.add_argument('--password', help='SQL Server password')
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
    
    # Enable CDC on the database
    if not enable_cdc_on_database(DB_CONFIG['database']):
        logger.error("Failed to enable CDC on database, exiting")
        sys.exit(1)
    
    # Enable CDC on key tables
    tables = [
        ('Insurance', 'Members'),
        ('Insurance', 'CoveragePlans'),
        ('Insurance', 'Policies'),
        ('Insurance', 'PolicyMembers'),
        ('Insurance', 'Providers'),
        ('Insurance', 'Claims'),
        ('Insurance', 'PremiumPayments'),
        ('Regulatory', 'PHIRebateTiers'),
        ('Regulatory', 'MBSItems'),
        ('Integration', 'SyntheaPatients'),
        ('Integration', 'SyntheaEncounters'),
        ('Integration', 'SyntheaProcedures')
    ]
    
    for schema, table in tables:
        enable_cdc_on_table(schema, table)
    
    logger.info("CDC setup completed successfully")

if __name__ == '__main__':
    main()