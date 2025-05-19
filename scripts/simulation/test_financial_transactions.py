#!/usr/bin/env python3
"""
Test the financial transaction generator to ensure it works correctly.
"""
import os
import sys
from datetime import date

# Add the parent directory to the path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from health_insurance_au.data_generation.financial_transactions import FinancialTransactionGenerator
from health_insurance_au.utils.logging_config import configure_logging, get_logger

# Set up logging
configure_logging()
logger = get_logger(__name__)

def test_financial_transactions():
    """Test the financial transaction generator."""
    logger.info("Testing financial transaction generator...")
    
    # Create a generator
    generator = FinancialTransactionGenerator()
    
    # Generate transactions for today
    today = date.today()
    result = generator.generate_transactions(today, detail_level=3)
    
    logger.info(f"Generated {result.get('transactions_generated', 0)} financial transactions")
    
    return result.get('transactions_generated', 0) > 0

def main():
    """Main entry point for the script."""
    success = test_financial_transactions()
    if success:
        logger.info("Financial transaction generator test passed!")
    else:
        logger.warning("Financial transaction generator test failed - no transactions generated")

if __name__ == '__main__':
    main()