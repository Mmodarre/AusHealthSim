# Change Data Capture (CDC) Guide

This document provides detailed information about the Change Data Capture (CDC) functionality in the Australian Health Insurance Simulation project.

## Overview

Change Data Capture (CDC) is a SQL Server feature that captures insert, update, and delete operations applied to SQL Server tables, making the details of the changes available in relational tables. This project uses CDC to track changes to the database, which is useful for:

- Data warehouse ETL processes
- Audit trails
- Historical analysis
- Incremental data loading

## CDC Setup

### Prerequisites

- SQL Server Enterprise, Developer, or Standard edition
- SQL Server Agent must be running
- Appropriate permissions (sysadmin or db_owner)

### Enabling CDC

To enable CDC on the database and tables, use the `enable_cdc.py` script:

```bash
python enable_cdc.py
```

Or use the shell script wrapper:

```bash
./enable_cdc.sh
```

This script will:

1. Enable CDC on the database using `sys.sp_cdc_enable_db`
2. Enable CDC on all relevant tables using `sys.sp_cdc_enable_table`

The following tables are configured for CDC:

- Insurance.Members
- Insurance.CoveragePlans
- Insurance.Policies
- Insurance.PolicyMembers
- Insurance.Providers
- Insurance.Claims
- Insurance.PremiumPayments
- Regulatory.PHIRebateTiers
- Regulatory.MBSItems
- Integration.SyntheaPatients
- Integration.SyntheaEncounters
- Integration.SyntheaProcedures

### CDC Table Structure

For each table enabled for CDC, SQL Server creates:

- A capture instance (default: `all`)
- CDC-specific tables in the `cdc` schema (e.g., `cdc.Insurance_Members_CT`)
- CDC-specific stored procedures for administration

Each CDC table contains:

- `__$start_lsn`: Log sequence number where the change begins
- `__$end_lsn`: Log sequence number where the change ends (NULL for active records)
- `__$seqval`: Sequence value for ordering changes
- `__$operation`: Type of operation (1=delete, 2=insert, 3=update before, 4=update after)
- `__$update_mask`: Bitmap of updated columns
- All columns from the source table
- `__$command_id`: ID of the command that made the change

## Monitoring CDC Changes

### Using the Monitor Script

To monitor CDC changes, use the `monitor_cdc.py` script:

```bash
python monitor_cdc.py --schema Insurance --table Members --hours 24
```

Or use the shell script wrapper:

```bash
./monitor_cdc.sh --schema Insurance --table Members --hours 24
```

Options:

- `--schema`: Schema name (default: Insurance)
- `--table`: Table name (default: Members)
- `--hours`: Number of hours to look back (default: 24)
- `--list-tables`: List all tables with CDC enabled
- `--net-changes`: Show only net changes (final state of each row)

### Programmatic Access

The project includes utility functions in `health_insurance_au/utils/cdc_utils.py` for working with CDC data:

- `get_cdc_changes()`: Get all changes from CDC
- `get_cdc_net_changes()`: Get net changes (final state of each row)
- `list_cdc_tables()`: List all tables with CDC enabled

Example usage:

```python
from health_insurance_au.utils.cdc_utils import get_cdc_changes, get_cdc_net_changes, list_cdc_tables

# List all CDC-enabled tables
cdc_tables = list_cdc_tables()
print(f"CDC is enabled on {len(cdc_tables)} tables")

# Get all changes for the Members table in the last 24 hours
changes = get_cdc_changes(schema_name='Insurance', table_name='Members', hours=24)
print(f"Found {len(changes)} changes")

# Get net changes (final state of each row) for the Members table in the last 24 hours
net_changes = get_cdc_net_changes(schema_name='Insurance', table_name='Members', hours=24)
print(f"Found {len(net_changes)} net changes")
```

## Report Generation

The CDC monitoring functionality can generate reports in CSV format:

- `direct_cdc_report`: Generates CSV files with schema, table, operation, record_id, and change_time
- `members_cdc_report`: Generates CSV files with member_id, operation, first_name, last_name, email, and change_time

These reports are saved in the `reports` directory by default.

## Best Practices

- Regularly clean up old CDC data using SQL Server's built-in cleanup job
- Monitor CDC table sizes to prevent excessive growth
- Use net changes for ETL processes to reduce processing overhead
- Consider enabling compression on CDC tables for large datasets

## Troubleshooting

### Common Issues

- **CDC not capturing changes**: Ensure SQL Server Agent is running
- **Missing CDC tables**: Verify CDC is enabled on both the database and the specific tables
- **Performance issues**: Consider adjusting the CDC cleanup job to run more frequently
- **Error accessing CDC tables**: Check permissions; users need SELECT permission on CDC tables

### Verifying CDC Status

To verify CDC is enabled on the database:

```sql
SELECT name, is_cdc_enabled
FROM sys.databases
WHERE name = 'HealthInsuranceAU';
```

To verify CDC is enabled on specific tables:

```sql
SELECT s.name AS schema_name, t.name AS table_name, t.is_tracked_by_cdc
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE t.is_tracked_by_cdc = 1;
```

## Additional Resources

- [SQL Server CDC Documentation](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server)
- [CDC Best Practices](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/administer-and-monitor-change-data-capture-sql-server)