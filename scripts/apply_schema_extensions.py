#!/usr/bin/env python3
"""
Script to apply database schema extensions for enhanced simulation.
"""
import os
import sys
import argparse
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from health_insurance_au.utils.db_utils import execute_non_query
from health_insurance_au.utils.logging_config import configure_logging, get_logger

# Set up logging
configure_logging()
logger = get_logger(__name__)

def read_sql_file(file_path):
    """Read SQL statements from a file."""
    with open(file_path, 'r') as f:
        sql_content = f.read()
    
    # Split by semicolons to get individual statements
    statements = sql_content.split(';')
    
    # Filter out empty statements
    statements = [stmt.strip() for stmt in statements if stmt.strip()]
    
    return statements

def main():
    """Main function to apply database schema extensions."""
    parser = argparse.ArgumentParser(description='Apply database schema extensions for enhanced simulation')
    parser.add_argument('--sql-file', default='scripts/extend_database_schema.sql', help='Path to SQL file with schema extensions')
    args = parser.parse_args()
    
    try:
        # Read SQL statements from file
        sql_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', args.sql_file))
        logger.info(f"Reading SQL statements from {sql_file_path}")
        
        if not os.path.exists(sql_file_path):
            logger.error(f"SQL file not found: {sql_file_path}")
            sys.exit(1)
        
        statements = read_sql_file(sql_file_path)
        logger.info(f"Found {len(statements)} SQL statements")
        
        # Execute each statement
        for i, stmt in enumerate(statements, 1):
            logger.info(f"Executing statement {i} of {len(statements)}")
            try:
                execute_non_query(stmt)
                logger.info(f"Statement {i} executed successfully")
            except Exception as e:
                logger.error(f"Error executing statement {i}: {e}")
                logger.error(f"Statement: {stmt[:100]}...")
                
                # Ask if we should continue
                if input("Continue with next statement? (y/n): ").lower() != 'y':
                    logger.info("Aborting execution")
                    break
        
        logger.info("Database schema extensions applied successfully")
    except Exception as e:
        logger.error(f"Error applying database schema extensions: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()