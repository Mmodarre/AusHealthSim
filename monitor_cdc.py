"""
Monitor CDC changes in the Health Insurance AU database using pyodbc.
"""
import argparse
import logging
from datetime import datetime, timedelta
import json
import os

from health_insurance_au.utils.cdc_utils import get_cdc_changes, get_cdc_net_changes, list_cdc_tables
from health_insurance_au.utils.logging_config import configure_logging, get_logger
from health_insurance_au.config import LOG_CONFIG

# Set up logging
logger = get_logger(__name__)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Monitor CDC changes in the Health Insurance AU database')
    parser.add_argument('--schema', default='Insurance', help='Schema name')
    parser.add_argument('--table', default='Members', help='Table name')
    parser.add_argument('--hours', type=int, default=24, help='Number of hours to look back')
    parser.add_argument('--list-tables', action='store_true', help='List all tables with CDC enabled')
    parser.add_argument('--net-changes', action='store_true', help='Show only net changes')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
                        default=os.environ.get('HEALTH_INSURANCE_LOG_LEVEL', LOG_CONFIG['default_level']),
                        help='Set the logging level')
    parser.add_argument('--log-file', help='Log to this file (in addition to console)')
    
    args = parser.parse_args()
    
    # Configure logging based on command line arguments
    log_file = args.log_file if args.log_file else None
    if log_file is None and LOG_CONFIG.get('log_file'):
        # Use default log file from config if not specified and config has one
        log_file = os.path.join(LOG_CONFIG['log_dir'], LOG_CONFIG['log_file'])
    
    configure_logging(level=args.log_level, log_file=log_file)
    
    
    if args.list_tables:
        logger.info("Listing tables with CDC enabled...")
        tables = list_cdc_tables()
        if tables:
            logger.info(f"Found {len(tables)} tables with CDC enabled:")
            for table in tables:
                logger.info(f"  {table['schema_name']}.{table['table_name']} ({table['capture_instance']})")
        else:
            logger.info("No tables with CDC enabled found.")
        return
    
    # Calculate the time range
    to_time = datetime.now()
    from_time = to_time - timedelta(hours=args.hours)
    
    logger.info(f"Monitoring CDC changes for {args.schema}.{args.table}")
    logger.info(f"Time range: {from_time} to {to_time}")
    
    if args.net_changes:
        changes = get_cdc_net_changes(args.schema, args.table, from_time, to_time)
        logger.info(f"Found {len(changes)} net changes")
    else:
        changes = get_cdc_changes(args.schema, args.table, from_time, to_time)
        logger.info(f"Found {len(changes)} changes")
    
    if changes:
        # Pretty print the first 5 changes
        for i, change in enumerate(changes[:5]):
            logger.info(f"Change {i+1}:")
            for key, value in change.items():
                logger.info(f"  {key}: {value}")
        
        if len(changes) > 5:
            logger.info(f"... and {len(changes) - 5} more changes")
        
        # Save all changes to a file
        output_file = f"cdc_changes_{args.schema}_{args.table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(changes, f, default=str, indent=2)
        
        logger.info(f"All changes saved to {output_file}")
    else:
        logger.info("No changes found in the specified time range")

if __name__ == '__main__':
    main()