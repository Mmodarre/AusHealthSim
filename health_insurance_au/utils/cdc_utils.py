"""
Utilities for working with Change Data Capture (CDC) in the Health Insurance AU database.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from health_insurance_au.utils.db_utils import execute_query
from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

def get_cdc_changes(schema_name: str, table_name: str, 
                    from_time: Optional[datetime] = None, 
                    to_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Get changes from CDC for a specific table between two points in time.
    
    Args:
        schema_name: The schema name of the table
        table_name: The table name
        from_time: The start time for changes (default: 24 hours ago)
        to_time: The end time for changes (default: current time)
        
    Returns:
        A list of dictionaries representing the changes
    """
    # Set default times if not provided
    if from_time is None:
        from_time = datetime.now() - timedelta(days=1)
    
    if to_time is None:
        to_time = datetime.now()
    
    # Convert datetime to SQL Server datetime string
    from_time_str = from_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    to_time_str = to_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    # Get the LSN range for the time period
    lsn_query = f"""
    DECLARE @from_lsn binary(10), @to_lsn binary(10);
    
    -- Get the LSNs for the time range
    SET @from_lsn = sys.fn_cdc_map_time_to_lsn('smallest greater than or equal', '{from_time_str}');
    SET @to_lsn = sys.fn_cdc_map_time_to_lsn('largest less than or equal', '{to_time_str}');
    
    -- Return the LSNs as strings
    SELECT 
        CONVERT(nvarchar(23), @from_lsn, 1) as from_lsn,
        CONVERT(nvarchar(23), @to_lsn, 1) as to_lsn;
    """
    
    lsn_result = execute_query(lsn_query)
    
    if not lsn_result:
        logger.error("Failed to get LSN range")
        return []
    
    from_lsn = lsn_result[0].get('from_lsn')
    to_lsn = lsn_result[0].get('to_lsn')
    
    if not from_lsn or not to_lsn:
        logger.error("Invalid LSN range")
        return []
    
    # Get the CDC capture instance name
    instance_query = f"""
    SELECT capture_instance FROM cdc.change_tables
    WHERE source_schema_name = '{schema_name}'
    AND source_name = '{table_name}'
    """
    
    instance_result = execute_query(instance_query)
    
    if not instance_result:
        logger.error(f"No CDC capture instance found for {schema_name}.{table_name}")
        return []
    
    capture_instance = instance_result[0].get('capture_instance')
    
    if not capture_instance:
        logger.error(f"Invalid CDC capture instance for {schema_name}.{table_name}")
        return []
    
    # Get the changes
    changes_query = f"""
    DECLARE @from_lsn binary(10), @to_lsn binary(10);
    
    -- Convert string LSNs back to binary
    SET @from_lsn = CONVERT(binary(10), '{from_lsn}', 1);
    SET @to_lsn = CONVERT(binary(10), '{to_lsn}', 1);
    
    -- Get all changes
    SELECT * FROM cdc.fn_cdc_get_all_changes_{capture_instance}(@from_lsn, @to_lsn, 'all');
    """
    
    changes = execute_query(changes_query)
    
    return changes

def get_cdc_net_changes(schema_name: str, table_name: str, 
                         from_time: Optional[datetime] = None, 
                         to_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Get net changes from CDC for a specific table between two points in time.
    Net changes show only the final state of each row that changed.
    
    Args:
        schema_name: The schema name of the table
        table_name: The table name
        from_time: The start time for changes (default: 24 hours ago)
        to_time: The end time for changes (default: current time)
        
    Returns:
        A list of dictionaries representing the net changes
    """
    # Set default times if not provided
    if from_time is None:
        from_time = datetime.now() - timedelta(days=1)
    
    if to_time is None:
        to_time = datetime.now()
    
    # Convert datetime to SQL Server datetime string
    from_time_str = from_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    to_time_str = to_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    # Get the LSN range for the time period
    lsn_query = f"""
    DECLARE @from_lsn binary(10), @to_lsn binary(10);
    
    -- Get the LSNs for the time range
    SET @from_lsn = sys.fn_cdc_map_time_to_lsn('smallest greater than or equal', '{from_time_str}');
    SET @to_lsn = sys.fn_cdc_map_time_to_lsn('largest less than or equal', '{to_time_str}');
    
    -- Return the LSNs as strings
    SELECT 
        CONVERT(nvarchar(23), @from_lsn, 1) as from_lsn,
        CONVERT(nvarchar(23), @to_lsn, 1) as to_lsn;
    """
    
    lsn_result = execute_query(lsn_query)
    
    if not lsn_result:
        logger.error("Failed to get LSN range")
        return []
    
    from_lsn = lsn_result[0].get('from_lsn')
    to_lsn = lsn_result[0].get('to_lsn')
    
    if not from_lsn or not to_lsn:
        logger.error("Invalid LSN range")
        return []
    
    # Get the CDC capture instance name
    instance_query = f"""
    SELECT capture_instance FROM cdc.change_tables
    WHERE source_schema_name = '{schema_name}'
    AND source_name = '{table_name}'
    """
    
    instance_result = execute_query(instance_query)
    
    if not instance_result:
        logger.error(f"No CDC capture instance found for {schema_name}.{table_name}")
        return []
    
    capture_instance = instance_result[0].get('capture_instance')
    
    if not capture_instance:
        logger.error(f"Invalid CDC capture instance for {schema_name}.{table_name}")
        return []
    
    # Get the net changes
    changes_query = f"""
    DECLARE @from_lsn binary(10), @to_lsn binary(10);
    
    -- Convert string LSNs back to binary
    SET @from_lsn = CONVERT(binary(10), '{from_lsn}', 1);
    SET @to_lsn = CONVERT(binary(10), '{to_lsn}', 1);
    
    -- Get net changes
    SELECT * FROM cdc.fn_cdc_get_net_changes_{capture_instance}(@from_lsn, @to_lsn, 'all');
    """
    
    changes = execute_query(changes_query)
    
    return changes

def list_cdc_tables() -> List[Dict[str, str]]:
    """
    List all tables that have CDC enabled.
    
    Returns:
        A list of dictionaries with schema_name and table_name
    """
    query = """
    SELECT 
        s.name AS schema_name,
        t.name AS table_name,
        ct.capture_instance
    FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    JOIN cdc.change_tables ct ON ct.source_object_id = t.object_id
    WHERE t.is_tracked_by_cdc = 1
    ORDER BY s.name, t.name
    """
    
    return execute_query(query)