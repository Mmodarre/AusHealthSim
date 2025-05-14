"""
Test script to verify pyodbc connection to the SQL Server.
"""
import sys
import os
import logging
import pyodbc
import argparse

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from health_insurance_au.utils.env_utils import get_db_config
from health_insurance_au.config import DB_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection(server=None, username=None, password=None, database=None, driver=None):
    """Test connection to the SQL Server."""
    try:
        # Use provided parameters or fall back to DB_CONFIG
        server = server or DB_CONFIG['server']
        database = database or DB_CONFIG['database']
        username = username or DB_CONFIG['username']
        password = password or DB_CONFIG['password']
        driver = driver or DB_CONFIG['driver']
        
        # Construct connection string
        conn_str = (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )
        
        logger.info(f"Connecting to SQL Server: {server}")
        logger.info(f"Database: {database}")
        logger.info(f"Driver: {driver}")
        
        # List available ODBC drivers
        logger.info("Available ODBC drivers:")
        for driver in pyodbc.drivers():
            logger.info(f"  {driver}")
        
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        logger.info("Connection successful!")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        logger.info(f"SQL Server version: {row[0]}")
        
        # Close the connection
        conn.close()
        logger.info("Connection closed")
        
        return True
    except pyodbc.Error as e:
        logger.error(f"Database connection error: {e}")
        return False

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Test pyodbc connection to SQL Server')
    parser.add_argument('--server', help='SQL Server address')
    parser.add_argument('--username', help='SQL Server username')
    parser.add_argument('--password', help='SQL Server password')
    parser.add_argument('--database', help='Database name')
    parser.add_argument('--driver', help='ODBC Driver name')
    parser.add_argument('--env-file', help='Path to environment file with database credentials')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
                        default='INFO', help='Set the logging level')
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Get database configuration from environment variables or file if env-file is specified
    if args.env_file:
        env_db_config = get_db_config(args.env_file)
        
        # Update DB_CONFIG with environment values
        if env_db_config['server']:
            DB_CONFIG['server'] = env_db_config['server']
        if env_db_config['database']:
            DB_CONFIG['database'] = env_db_config['database']
        if env_db_config['username']:
            DB_CONFIG['username'] = env_db_config['username']
        if env_db_config['password']:
            DB_CONFIG['password'] = env_db_config['password']
        if env_db_config['driver']:
            DB_CONFIG['driver'] = env_db_config['driver']
    
    # Test the connection with any provided command-line arguments
    test_connection(
        server=args.server,
        username=args.username,
        password=args.password,
        database=args.database,
        driver=args.driver
    )

if __name__ == '__main__':
    main()