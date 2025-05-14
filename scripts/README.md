# Scripts Directory

This directory contains Python scripts for various operations in the Health Insurance Simulation project.

## Directory Structure

- `db/` - Database-related scripts
  - `initialize_db.py` - Creates the database schema
  - `add_initial_data.py` - Adds initial data to the database
  - `enable_cdc.py` - Enables Change Data Capture on database tables
  - `check_db.py` - Checks database connectivity and status
  - `monitor_cdc.py` - Monitors CDC changes
  - `test_pyodbc.py` - Tests PyODBC connectivity

- `simulation/` - Simulation-related scripts
  - `realistic_simulation.py` - Runs a realistic simulation

- `utils/` - Utility scripts
  - `manage_used_members.py` - Manages the list of used members

## Usage

These scripts are typically called from shell scripts in the `bin/` directory, but can also be run directly:

```bash
python scripts/db/initialize_db.py --server <server> --database <database>
```

For more information on each script, run it with the `--help` flag:

```bash
python scripts/db/initialize_db.py --help
```