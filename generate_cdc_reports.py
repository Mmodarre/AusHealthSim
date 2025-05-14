"""
Generate reports from CDC changes in the Health Insurance AU database.
"""
import argparse
import logging
from datetime import datetime, timedelta
import json
import csv
import os

from health_insurance_au.utils.cdc_utils_pyodbc import get_cdc_net_changes, list_cdc_tables

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_daily_changes_report(date=None, output_dir='reports'):
    """
    Generate a report of all changes from the previous day.
    
    Args:
        date: The date to generate the report for (default: today)
        output_dir: Directory to save the report
    
    Returns:
        The path to the generated report file
    """
    if date is None:
        date = datetime.now()
    
    # Calculate the time range (previous day)
    to_time = date.replace(hour=23, minute=59, second=59)
    from_time = date.replace(hour=0, minute=0, second=0)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all tables with CDC enabled
    tables = list_cdc_tables()
    
    if not tables:
        logger.warning("No tables with CDC enabled found.")
        return None
    
    # Create a report file
    report_file = os.path.join(output_dir, f'cdc_daily_changes_{date.strftime("%Y%m%d")}.csv')
    
    with open(report_file, 'w', newline='') as csvfile:
        fieldnames = ['schema', 'table', 'operation', 'record_count', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process each table
        for table in tables:
            schema_name = table['schema_name']
            table_name = table['table_name']
            
            logger.info(f"Processing changes for {schema_name}.{table_name}")
            
            # Get net changes for the table
            changes = get_cdc_net_changes(schema_name, table_name, from_time, to_time)
            
            if not changes:
                logger.info(f"No changes found for {schema_name}.{table_name}")
                continue
            
            # Count operations
            inserts = 0
            updates = 0
            deletes = 0
            
            for change in changes:
                operation = change.get('__$operation')
                if operation == '1':  # Delete
                    deletes += 1
                elif operation == '2':  # Insert
                    inserts += 1
                elif operation == '4':  # Update
                    updates += 1
            
            # Write to the report
            if inserts > 0:
                writer.writerow({
                    'schema': schema_name,
                    'table': table_name,
                    'operation': 'INSERT',
                    'record_count': inserts,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            
            if updates > 0:
                writer.writerow({
                    'schema': schema_name,
                    'table': table_name,
                    'operation': 'UPDATE',
                    'record_count': updates,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            
            if deletes > 0:
                writer.writerow({
                    'schema': schema_name,
                    'table': table_name,
                    'operation': 'DELETE',
                    'record_count': deletes,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
    
    logger.info(f"Daily changes report generated: {report_file}")
    return report_file

def generate_member_changes_report(days=7, output_dir='reports'):
    """
    Generate a report of member changes over a period of days.
    
    Args:
        days: Number of days to look back
        output_dir: Directory to save the report
        
    Returns:
        The path to the generated report file
    """
    # Calculate the time range
    to_time = datetime.now()
    from_time = to_time - timedelta(days=days)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get member changes
    changes = get_cdc_net_changes('Insurance', 'Members', from_time, to_time)
    
    if not changes:
        logger.warning(f"No member changes found in the last {days} days.")
        return None
    
    # Create a report file
    report_file = os.path.join(output_dir, f'member_changes_last_{days}_days.csv')
    
    # Extract relevant fields
    with open(report_file, 'w', newline='') as csvfile:
        fieldnames = ['MemberID', 'FirstName', 'LastName', 'Email', 'State', 'Operation', 'ChangeDate']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for change in changes:
            operation = change.get('__$operation')
            op_name = 'DELETE' if operation == '1' else 'INSERT' if operation == '2' else 'UPDATE'
            
            writer.writerow({
                'MemberID': change.get('MemberID', ''),
                'FirstName': change.get('FirstName', ''),
                'LastName': change.get('LastName', ''),
                'Email': change.get('Email', ''),
                'State': change.get('State', ''),
                'Operation': op_name,
                'ChangeDate': change.get('__$start_lsn', '')
            })
    
    logger.info(f"Member changes report generated: {report_file}")
    return report_file

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Generate reports from CDC changes')
    parser.add_argument('--report-type', choices=['daily', 'members'], default='daily',
                        help='Type of report to generate')
    parser.add_argument('--days', type=int, default=7,
                        help='Number of days to look back for member changes report')
    parser.add_argument('--date', help='Date for daily report (YYYY-MM-DD)')
    parser.add_argument('--output-dir', default='reports',
                        help='Directory to save the report')
    
    args = parser.parse_args()
    
    if args.report_type == 'daily':
        date = None
        if args.date:
            try:
                date = datetime.strptime(args.date, '%Y-%m-%d')
            except ValueError:
                logger.error(f"Invalid date format: {args.date}. Expected YYYY-MM-DD.")
                return
        
        report_file = generate_daily_changes_report(date, args.output_dir)
        
    elif args.report_type == 'members':
        report_file = generate_member_changes_report(args.days, args.output_dir)
    
    if report_file:
        logger.info(f"Report generated successfully: {report_file}")
    else:
        logger.warning("No report generated.")

if __name__ == '__main__':
    main()