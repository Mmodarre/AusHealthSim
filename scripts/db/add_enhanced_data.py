#!/usr/bin/env python3
"""
Script to add initial data for enhanced simulation tables.
"""
import os
import sys
import argparse
from datetime import datetime, date
from pathlib import Path

# Add the parent directory to the path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

from health_insurance_au.utils.db_utils import execute_non_query, bulk_insert, execute_query
from health_insurance_au.utils.env_utils import get_db_config
from health_insurance_au.utils.logging_config import configure_logging, get_logger

# Set up logging
configure_logging()
logger = get_logger(__name__)

def add_fraud_indicators():
    """Add initial fraud indicators to the database."""
    logger.info("Adding initial fraud indicators...")
    
    indicators = [
        {
            'IndicatorCode': 'DUP_CLAIM',
            'IndicatorName': 'Duplicate Claim',
            'IndicatorDescription': 'Multiple claims for the same service on the same date',
            'SeverityLevel': 'High',
            'DetectionLogic': 'Claims with identical service dates, service descriptions, and member IDs within a 30-day period'
        },
        {
            'IndicatorCode': 'FREQ_CLAIM',
            'IndicatorName': 'High Frequency Claims',
            'IndicatorDescription': 'Unusually high number of claims in a short period',
            'SeverityLevel': 'Medium',
            'DetectionLogic': 'More than 5 claims for the same member within a 30-day period'
        },
        {
            'IndicatorCode': 'UNBUNDLING',
            'IndicatorName': 'Service Unbundling',
            'IndicatorDescription': 'Multiple claims for services that should be bundled',
            'SeverityLevel': 'High',
            'DetectionLogic': 'Multiple related procedure codes submitted separately on the same date'
        },
        {
            'IndicatorCode': 'UPCODING',
            'IndicatorName': 'Upcoding',
            'IndicatorDescription': 'Using a higher-paying code than the service provided',
            'SeverityLevel': 'High',
            'DetectionLogic': 'Consistent pattern of using higher complexity codes than peer average'
        },
        {
            'IndicatorCode': 'PHANTOM_BILL',
            'IndicatorName': 'Phantom Billing',
            'IndicatorDescription': 'Billing for services not provided',
            'SeverityLevel': 'Critical',
            'DetectionLogic': 'Claims for services that conflict with other recorded patient activities'
        }
    ]
    
    try:
        rows_affected = bulk_insert("Insurance.FraudIndicators", indicators)
        logger.info(f"Added {rows_affected} fraud indicators")
    except Exception as e:
        logger.error(f"Error adding fraud indicators: {e}")
        raise

def add_actuarial_metrics():
    """Add initial actuarial metrics to the database."""
    logger.info("Adding initial actuarial metrics...")
    
    today = date.today()
    
    metrics = [
        {
            'MetricDate': today,
            'MetricType': 'Loss Ratio',
            'MetricCategory': 'Hospital',
            'MetricValue': 0.82,
            'AgeGroup': '18-30',
            'Gender': 'M',
            'StateTerritory': 'NSW',
            'ProductCategory': 'Gold',
            'RiskSegment': 'Low'
        },
        {
            'MetricDate': today,
            'MetricType': 'Loss Ratio',
            'MetricCategory': 'Hospital',
            'MetricValue': 0.78,
            'AgeGroup': '18-30',
            'Gender': 'F',
            'StateTerritory': 'NSW',
            'ProductCategory': 'Gold',
            'RiskSegment': 'Low'
        },
        {
            'MetricDate': today,
            'MetricType': 'Lapse Rate',
            'MetricCategory': 'Hospital',
            'MetricValue': 0.12,
            'AgeGroup': '18-30',
            'Gender': 'M',
            'StateTerritory': 'NSW',
            'ProductCategory': 'Gold',
            'RiskSegment': 'Low'
        },
        {
            'MetricDate': today,
            'MetricType': 'Acquisition Cost',
            'MetricCategory': 'Hospital',
            'MetricValue': 320.50,
            'AgeGroup': '18-30',
            'Gender': None,  # Explicitly set to None for nullable fields
            'StateTerritory': None,
            'ProductCategory': 'Gold',
            'RiskSegment': None
        },
        {
            'MetricDate': today,
            'MetricType': 'Retention Cost',
            'MetricCategory': 'Hospital',
            'MetricValue': 85.50,
            'AgeGroup': '18-30',
            'Gender': None,  # Explicitly set to None for nullable fields
            'StateTerritory': None,
            'ProductCategory': 'Gold',
            'RiskSegment': None
        }
    ]
    
    try:
        rows_affected = bulk_insert("Insurance.ActuarialMetrics", metrics)
        logger.info(f"Added {rows_affected} actuarial metrics")
    except Exception as e:
        logger.error(f"Error adding actuarial metrics: {e}")
        raise

def main():
    """Main function to add enhanced initial data."""
    parser = argparse.ArgumentParser(description='Add initial data for enhanced simulation tables')
    parser.add_argument('--server', help='SQL Server address')
    parser.add_argument('--username', help='SQL Server username')
    parser.add_argument('--password', help='SQL Server password')
    parser.add_argument('--database', help='Database name')
    parser.add_argument('--env-file', help='Path to environment file with database credentials')
    
    args = parser.parse_args()
    
    # Get database configuration from environment variables or file
    db_config = get_db_config(args.env_file)
    
    # Override with provided arguments if any
    if args.server:
        db_config['server'] = args.server
    if args.username:
        db_config['username'] = args.username
    if args.password:
        db_config['password'] = args.password
    if args.database:
        db_config['database'] = args.database
    
    try:
        # Check if tables already have data
        logger.info("Checking if tables already have data...")
        
        fraud_count = execute_query("SELECT COUNT(*) AS count FROM Insurance.FraudIndicators")
        logger.info(f"Fraud indicators query result: {fraud_count}")
        
        actuarial_count = execute_query("SELECT COUNT(*) AS count FROM Insurance.ActuarialMetrics")
        logger.info(f"Actuarial metrics query result: {actuarial_count}")
        
        if fraud_count and fraud_count[0].get('count', 0) > 0:
            logger.info(f"Found {fraud_count[0]['count']} existing fraud indicators, skipping insertion")
        else:
            logger.info("No existing fraud indicators found, adding new ones...")
            add_fraud_indicators()
            
        if actuarial_count and actuarial_count[0].get('count', 0) > 0:
            logger.info(f"Found {actuarial_count[0]['count']} existing actuarial metrics, skipping insertion")
        else:
            logger.info("No existing actuarial metrics found, adding new ones...")
            add_actuarial_metrics()
            
        logger.info("Enhanced initial data check completed successfully")
    except Exception as e:
        logger.error(f"Error adding enhanced initial data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()