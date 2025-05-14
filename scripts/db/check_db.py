"""
Check the database structure.
"""
import subprocess
import sys
import os
import argparse

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from health_insurance_au.utils.env_utils import get_db_config

def run_sql_command(server, username, password, database, query):
    """Run a SQL command using sqlcmd."""
    cmd = [
        'sqlcmd',
        '-S', server,
        '-U', username,
        '-P', password,
        '-d', database,
        '-Q', query,
        '-h', '-1',  # No headers
        '-W',  # Remove trailing spaces
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"SQL command error: {e}")
        print(f"stderr: {e.stderr}")
        return None

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Check the database structure')
    parser.add_argument('--server', help='SQL Server address')
    parser.add_argument('--username', help='SQL Server username')
    parser.add_argument('--password', help='SQL Server password')
    parser.add_argument('--database', help='Database name')
    parser.add_argument('--env-file', help='Path to environment file with database credentials')
    
    args = parser.parse_args()
    
    # Get database configuration from environment variables or file
    db_config = get_db_config(args.env_file)
    print(db_config)
    
    # Override with command-line arguments if provided
    server = args.server or db_config['server']
    username = args.username or db_config['username']
    password = args.password or db_config['password']
    database = args.database or db_config['database']
    
    # Validate required parameters
    if not server:
        print("Error: Server address is required")
        return
    if not username:
        print("Error: Username is required")
        return
    if not password:
        print("Error: Password is required")
        return
    if not database:
        print("Error: Database name is required")
        return
    
    # Check members
    print("Checking Members table...")
    result = run_sql_command(
        server, username, password, database,
        "SELECT TOP 1 * FROM Insurance.Members"
    )
    print(result)
    
    # Check coverage plans
    print("\nChecking CoveragePlans table...")
    result = run_sql_command(
        server, username, password, database,
        "SELECT TOP 1 * FROM Insurance.CoveragePlans"
    )
    print(result)
    
    # Check providers
    print("\nChecking Providers table...")
    result = run_sql_command(
        server, username, password, database,
        "SELECT TOP 1 * FROM Insurance.Providers"
    )
    print(result)

if __name__ == '__main__':
    main()