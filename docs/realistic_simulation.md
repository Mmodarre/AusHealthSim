# Realistic Health Insurance Simulation

This script provides a realistic simulation of health insurance operations, generating data for members joining, leaving, making claims, and other insurance activities between a specified start and end date.

## Features

- Simulates daily health insurance operations with realistic parameters
- Automatically adjusts simulation parameters based on the number of new members
- Includes weekly and monthly patterns (fewer members on weekends, more claims at the beginning/end of month)
- Generates random datetimes for events (during business hours)
- Tracks used members to ensure each member from the source data is only used once
- Supports customizable logging levels

## Usage

### Using the Shell Script

```bash
./run_realistic_simulation.sh --start-date 2023-01-01 --end-date 2023-01-31 --members-per-day 10
```

Options:
- `--start-date`: Start date for the simulation (YYYY-MM-DD) [required]
- `--end-date`: End date for the simulation (YYYY-MM-DD) [required]
- `--members-per-day`: Base number of new members per day (default: 10)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) (default: INFO)
- `--env-file`: Path to environment file with database configuration
- `--reset-members`: Reset the list of used member IDs before running the simulation

### Using the Python Script Directly

```bash
python3 realistic_simulation.py --start-date 2023-01-01 --end-date 2023-01-31 --members-per-day 10
```

### Managing Used Members

The simulation keeps track of which members from the source data have been used to prevent duplicates. You can manage this list using the `manage_used_members.py` script:

```bash
# Show the list of used member IDs
./manage_used_members.py show

# Reset the list of used member IDs
./manage_used_members.py reset
```

## How It Works

1. For each day in the simulation period:
   - Calculates realistic parameters based on the number of new members
   - Adjusts parameters based on the day of the week and month
   - Generates random datetimes for all events during business hours
   - Runs the daily simulation with the calculated parameters

2. The simulation generates:
   - New members joining the insurance
   - New policies being created
   - Member information updates
   - Policy changes
   - Hospital claims
   - General treatment claims
   - Premium payments
   - Claim processing

## Simulation Parameters

The script automatically calculates realistic parameters based on the number of new members:

- New policies: 60-80% of new members
- Member updates: 1-3% of existing members
- Policy changes: 0.5-1.5% of existing policies
- Hospital claims: 10-20% of new members
- General claims: 30-50% of new members
- Claims processing: 75-95% of submitted claims

## Weekly and Monthly Patterns

- Weekends: Fewer members join (60% of weekday rate)
- Beginning/End of month: More claims (120% of mid-month rate)

## Requirements

- Python 3.6+
- SQL Server database with the Health Insurance AU schema
- Database connection details in environment variables or config file