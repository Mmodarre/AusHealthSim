#!/usr/bin/env python3
"""
Execute SQL scripts from file.
"""
import argparse
import sys
import os
import pyodbc
from contextlib import contextmanager
from pathlib import Path

# Add the parent directory to the path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

from health_insurance_au.utils.env_utils import get_db_config
from health_insurance_au.utils.logging_config import configure_logging, get_logger

# Set up logging
configure_logging()
logger = get_logger(__name__)

@contextmanager
def get_connection(server, username, password, database=None):
    """Context manager for database connections."""
    # Construct connection string with the correct driver name
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};UID={username};PWD={password};TrustServerCertificate=yes"
    if database:
        conn_str += f";DATABASE={database}"
    
    conn = None
    try:
        conn = pyodbc.connect(conn_str, autocommit=True)  # Set autocommit to True
        yield conn
    except pyodbc.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def execute_sql_script(sql_file, server=None, database=None, username=None, password=None, config_path=None):
    """
    Execute a SQL script file.
    
    Args:
        sql_file: Path to the SQL script file
        server: SQL Server address
        database: Database name
        username: SQL Server username
        password: SQL Server password
        config_path: Path to config file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get database configuration from environment variables or file
        db_config = get_db_config(config_path)
        
        # Override with provided arguments if any
        server = server or db_config['server']
        username = username or db_config['username']
        password = password or db_config['password']
        database = database or db_config['database']
        
        # Validate required parameters
        if not server:
            logger.error("Server address is required")
            return False
        if not username:
            logger.error("Username is required")
            return False
        if not password:
            logger.error("Password is required")
            return False
        if not database:
            logger.error("Database name is required")
            return False
        
        # Read the SQL script file
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        # Split script by GO statements (common in SQL Server scripts)
        statements = sql_script.split("GO")
        
        # Execute each statement
        with get_connection(server, username, password, database) as conn:
            for statement in statements:
                if statement.strip():
                    try:
                        cursor = conn.cursor()
                        cursor.execute(statement)
                        # No need to commit with autocommit=True
                    except pyodbc.Error as e:
                        logger.error(f"SQL script execution error: {e}")
                        logger.error(f"Failed statement: {statement}")
                        return False
        
        logger.info(f"SQL script {sql_file} executed successfully")
        return True
    except Exception as e:
        logger.error(f"Error executing SQL script: {e}")
        return False

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Execute SQL scripts')
    parser.add_argument('sql_file', help='SQL script file to execute')
    parser.add_argument('--server', help='SQL Server address')
    parser.add_argument('--username', help='SQL Server username')
    parser.add_argument('--password', help='SQL Server password')
    parser.add_argument('--database', help='Database name')
    parser.add_argument('--env-file', help='Path to environment file with database credentials')
    
    args = parser.parse_args()
    
    # Call the execute_sql_script function
    success = execute_sql_script(
        sql_file=args.sql_file,
        server=args.server,
        database=args.database,
        username=args.username,
        password=args.password,
        config_path=args.env_file
    )
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()