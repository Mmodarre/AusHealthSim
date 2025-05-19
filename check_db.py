#!/usr/bin/env python3
"""
Script to check database structure
"""
import os
import pyodbc
from dotenv import load_dotenv

# Load environment variables from config/db_config.env
load_dotenv('config/db_config.env')

# Get database connection details from environment variables
server = os.getenv('DB_SERVER', '135.119.136.29')
database = os.getenv('DB_DATABASE', 'aushealthsim')
username = os.getenv('DB_USERNAME', 'mehdi')
password = os.getenv('DB_PASSWORD', 'SanjabV-MM369')
driver = os.getenv('DB_DRIVER', '{ODBC Driver 17 for SQL Server}')

# Construct connection string
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes'

print(f'Connecting to {server}, {database}...')

try:
    # Connect to the database
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Get all tables
    print("\n=== Tables ===")
    cursor.execute('SELECT SCHEMA_NAME(schema_id) as schema_name, name FROM sys.tables ORDER BY schema_name, name')
    tables = cursor.fetchall()
    for schema, table in tables:
        print(f"{schema}.{table}")
    
    # Get all columns for Insurance.Members
    print("\n=== Insurance.Members Columns ===")
    cursor.execute("""
        SELECT c.name, t.name as type_name, c.max_length, c.is_nullable
        FROM sys.columns c
        JOIN sys.types t ON c.user_type_id = t.user_type_id
        JOIN sys.tables tbl ON c.object_id = tbl.object_id
        JOIN sys.schemas s ON tbl.schema_id = s.schema_id
        WHERE s.name = 'Insurance' AND tbl.name = 'Members'
        ORDER BY c.column_id
    """)
    columns = cursor.fetchall()
    for name, type_name, max_length, is_nullable in columns:
        nullable = "NULL" if is_nullable else "NOT NULL"
        print(f"{name}: {type_name}({max_length}) {nullable}")
    
    # Get all columns for Insurance.Policies
    print("\n=== Insurance.Policies Columns ===")
    cursor.execute("""
        SELECT c.name, t.name as type_name, c.max_length, c.is_nullable
        FROM sys.columns c
        JOIN sys.types t ON c.user_type_id = t.user_type_id
        JOIN sys.tables tbl ON c.object_id = tbl.object_id
        JOIN sys.schemas s ON tbl.schema_id = s.schema_id
        WHERE s.name = 'Insurance' AND tbl.name = 'Policies'
        ORDER BY c.column_id
    """)
    columns = cursor.fetchall()
    for name, type_name, max_length, is_nullable in columns:
        nullable = "NULL" if is_nullable else "NOT NULL"
        print(f"{name}: {type_name}({max_length}) {nullable}")
    
    # Get all columns for Insurance.Claims
    print("\n=== Insurance.Claims Columns ===")
    cursor.execute("""
        SELECT c.name, t.name as type_name, c.max_length, c.is_nullable
        FROM sys.columns c
        JOIN sys.types t ON c.user_type_id = t.user_type_id
        JOIN sys.tables tbl ON c.object_id = tbl.object_id
        JOIN sys.schemas s ON tbl.schema_id = s.schema_id
        WHERE s.name = 'Insurance' AND tbl.name = 'Claims'
        ORDER BY c.column_id
    """)
    columns = cursor.fetchall()
    for name, type_name, max_length, is_nullable in columns:
        nullable = "NULL" if is_nullable else "NOT NULL"
        print(f"{name}: {type_name}({max_length}) {nullable}")
    
    # Get all columns for Insurance.Providers
    print("\n=== Insurance.Providers Columns ===")
    cursor.execute("""
        SELECT c.name, t.name as type_name, c.max_length, c.is_nullable
        FROM sys.columns c
        JOIN sys.types t ON c.user_type_id = t.user_type_id
        JOIN sys.tables tbl ON c.object_id = tbl.object_id
        JOIN sys.schemas s ON tbl.schema_id = s.schema_id
        WHERE s.name = 'Insurance' AND tbl.name = 'Providers'
        ORDER BY c.column_id
    """)
    columns = cursor.fetchall()
    for name, type_name, max_length, is_nullable in columns:
        nullable = "NULL" if is_nullable else "NOT NULL"
        print(f"{name}: {type_name}({max_length}) {nullable}")
    
    # Close the connection
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")