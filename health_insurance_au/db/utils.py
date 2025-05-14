"""
Database connection utilities for the Health Insurance AU simulation using pyodbc.
"""
import pyodbc
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager

from health_insurance_au.config import DB_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@contextmanager
def get_connection():
    """
    Context manager for database connections.
    
    Yields:
        A pyodbc connection object
    """
    # Construct connection string
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        f"TrustServerCertificate=yes;"
    )
    
    conn = None
    try:
        conn = pyodbc.connect(conn_str, autocommit=True)  # Set autocommit to True
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    """
    Execute a SQL query and return the results as a list of dictionaries.
    
    Args:
        query: The SQL query to execute
        params: Optional parameters for the query
        
    Returns:
        A list of dictionaries representing the query results
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            # Get column names from cursor description
            if cursor.description:
                column_names = [column[0] for column in cursor.description]
                
                # Fetch all rows and convert to dictionaries
                rows = []
                for row in cursor.fetchall():
                    # Convert row to dictionary
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[column_names[i]] = value
                    rows.append(row_dict)
                
                # Ensure we consume any remaining results to prevent "busy with results" errors
                while cursor.nextset():
                    pass
                
                return rows
            else:
                return []
    except Exception as e:
        logger.error(f"Database query error: {e}")
        return []

def execute_non_query(query: str, params: Optional[Tuple] = None, simulation_date: Optional[date] = None) -> int:
    """
    Execute a non-query SQL statement (INSERT, UPDATE, DELETE) and return the number of affected rows.
    
    Args:
        query: The SQL statement to execute
        params: Optional parameters for the statement
        simulation_date: The date to use for LastModified (if None, uses current date)
        
    Returns:
        The number of affected rows
    """
    try:
        # If simulation_date is provided and the query contains GETDATE(), replace it
        if simulation_date and 'GETDATE()' in query:
            formatted_date = simulation_date.strftime("'%Y-%m-%d'")
            query = query.replace('GETDATE()', f"CAST({formatted_date} AS DATETIME)")
        
        with get_connection() as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            # No need to commit with autocommit=True
            
            # Ensure we consume any remaining results to prevent "busy with results" errors
            while cursor.nextset():
                pass
                
            # Return the number of affected rows
            return cursor.rowcount
    except Exception as e:
        logger.error(f"Database non-query error: {e}")
        return 0

def execute_stored_procedure(proc_name: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Execute a stored procedure and return the results as a list of dictionaries.
    
    Args:
        proc_name: The name of the stored procedure to execute
        params: Optional parameters for the stored procedure as a dictionary
        
    Returns:
        A list of dictionaries representing the procedure results
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Construct the EXEC statement with parameters
            if params:
                # Create a list of parameter placeholders
                param_placeholders = []
                param_values = []
                
                for key, value in params.items():
                    param_placeholders.append(f"@{key}=?")
                    param_values.append(value)
                
                exec_statement = f"EXEC {proc_name} {', '.join(param_placeholders)}"
                cursor.execute(exec_statement, param_values)
            else:
                exec_statement = f"EXEC {proc_name}"
                cursor.execute(exec_statement)
            
            # Get results if any
            results = []
            
            # Process all result sets
            while True:
                if cursor.description:
                    column_names = [column[0] for column in cursor.description]
                    
                    for row in cursor.fetchall():
                        # Convert row to dictionary
                        row_dict = {}
                        for i, value in enumerate(row):
                            row_dict[column_names[i]] = value
                        results.append(row_dict)
                
                if not cursor.nextset():
                    break
            
            return results
    except Exception as e:
        logger.error(f"Database stored procedure error: {e}")
        return []

def bulk_insert(table_name: str, data: List[Dict[str, Any]], simulation_date: Optional[date] = None) -> int:
    """
    Perform a bulk insert operation.
    
    Args:
        table_name: The name of the table to insert into
        data: A list of dictionaries representing the rows to insert
        simulation_date: The date to use for LastModified (if None, uses current date)
        
    Returns:
        The number of inserted rows
    """
    if not data:
        return 0
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Get column names from the first dictionary
            columns = list(data[0].keys())
            
            # Check if LastModified column exists in the table
            has_last_modified = False
            table_info_query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name.split('.')[-1]}' AND COLUMN_NAME = 'LastModified'"
            cursor.execute(table_info_query)
            if cursor.fetchone():
                has_last_modified = True
            
            # If the table has LastModified and it's not in the data, add it
            if has_last_modified and 'LastModified' not in columns:
                # Add LastModified to each row with the simulation date or current date
                last_modified_value = simulation_date if simulation_date else datetime.now().date()
                for row in data:
                    row['LastModified'] = last_modified_value
                
                # Update columns list
                columns = list(data[0].keys())
            
            columns_str = ", ".join(columns)
            
            # Create placeholders for the VALUES clause
            placeholders = ", ".join(["?" for _ in columns])
            
            # Create the INSERT statement
            insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # Insert rows in batches
            rows_inserted = 0
            batch_size = 1000  # Adjust based on your needs
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i+batch_size]
                
                # Prepare batch parameters
                batch_params = []
                for row in batch:
                    # Create a list of values in the same order as columns
                    row_values = [row[col] for col in columns]
                    batch_params.append(tuple(row_values))
                
                # Execute many
                cursor.executemany(insert_sql, batch_params)
                # No need to commit with autocommit=True
                
                # Ensure we consume any remaining results to prevent "busy with results" errors
                while cursor.nextset():
                    pass
                
                rows_inserted += len(batch)
            
            return rows_inserted
    except Exception as e:
        logger.error(f"Database bulk insert error: {e}")
        return 0