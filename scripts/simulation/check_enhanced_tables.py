#!/usr/bin/env python3
"""
Check if data is being generated in the enhanced tables.
"""
import os
import sys
import argparse
from datetime import datetime

# Add the parent directory to the path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from health_insurance_au.utils.db_utils import execute_query
from health_insurance_au.utils.logging_config import configure_logging, get_logger

# Set up logging
configure_logging()
logger = get_logger(__name__)

def check_enhanced_tables():
    """Check if data is being generated in the enhanced tables."""
    try:
        # Check FinancialTransactions table
        transactions = execute_query("SELECT COUNT(*) AS count FROM Insurance.FinancialTransactions")
        transaction_count = transactions[0].get('count', 0) if transactions else 0
        logger.info(f"Found {transaction_count} records in FinancialTransactions table")
        
        if transaction_count > 0:
            # Get sample transactions
            sample_transactions = execute_query("SELECT TOP 5 * FROM Insurance.FinancialTransactions")
            logger.info("Sample transactions:")
            for transaction in sample_transactions:
                logger.info(f"  {transaction['TransactionType']} - {transaction['Amount']} - {transaction['TransactionDate']}")
        
        # Check ClaimPatterns table
        patterns = execute_query("SELECT COUNT(*) AS count FROM Insurance.ClaimPatterns")
        pattern_count = patterns[0].get('count', 0) if patterns else 0
        logger.info(f"Found {pattern_count} records in ClaimPatterns table")
        
        if pattern_count > 0:
            # Get sample patterns
            sample_patterns = execute_query("SELECT TOP 5 * FROM Insurance.ClaimPatterns")
            logger.info("Sample patterns:")
            for pattern in sample_patterns:
                logger.info(f"  {pattern['PatternType']} - {pattern['PatternDescription']} - {pattern['ConfidenceScore']}")
        
        # Check provider billing attributes
        providers = execute_query("""
            SELECT COUNT(*) AS count 
            FROM Insurance.Providers 
            WHERE BillingPatternScore IS NOT NULL
        """)
        provider_count = providers[0].get('count', 0) if providers else 0
        logger.info(f"Found {provider_count} providers with billing pattern attributes")
        
        if provider_count > 0:
            # Get sample providers
            sample_providers = execute_query("""
                SELECT TOP 5 ProviderName, BillingPatternScore, AvgClaimValue, ClaimFrequencyRating 
                FROM Insurance.Providers 
                WHERE BillingPatternScore IS NOT NULL
            """)
            logger.info("Sample providers with billing attributes:")
            for provider in sample_providers:
                logger.info(f"  {provider['ProviderName']} - Score: {provider['BillingPatternScore']} - Avg: {provider['AvgClaimValue']} - Freq: {provider['ClaimFrequencyRating']}")
        
        return transaction_count > 0 and pattern_count > 0 and provider_count > 0
    except Exception as e:
        logger.error(f"Error checking enhanced tables: {e}")
        return False

def main():
    """Main entry point for the script."""
    success = check_enhanced_tables()
    if success:
        logger.info("Enhanced tables have data!")
    else:
        logger.warning("One or more enhanced tables are empty or have issues")

if __name__ == '__main__':
    main()