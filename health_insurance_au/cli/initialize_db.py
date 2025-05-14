"""
Command-line interface for initializing the database.
"""
import argparse
import sys

from health_insurance_au.db import utils as db_utils

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Initialize the health insurance database")
    parser.add_argument("--server", help="SQL Server hostname")
    parser.add_argument("--database", help="Database name")
    parser.add_argument("--username", help="SQL Server username")
    parser.add_argument("--password", help="SQL Server password")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Initialize the database
    try:
        # Import the initialize_db function from the scripts module
        from scripts.db.initialize_db import initialize_database
        
        # Call the function with arguments from command line
        initialize_database(
            server=args.server,
            database=args.database,
            username=args.username,
            password=args.password,
            config_path=args.config,
            verbose=args.verbose
        )
        return 0
    except Exception as e:
        print(f"Error initializing database: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())