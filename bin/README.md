# Bin Directory

This directory contains shell scripts for running various operations in the Health Insurance Simulation project.

## Available Scripts

- `initialize_db.sh` - Creates the database schema
- `add_initial_data.sh` - Adds initial data to the database
- `enable_cdc.sh` - Enables Change Data Capture on database tables
- `run_simulation.sh` - Runs a basic simulation
- `run_realistic_simulation.sh` - Runs a more realistic simulation with parameters
- `run_complete_simulation.sh` - Runs a complete historical simulation
- `clean_and_reinstantiate.sh` - Cleans up and recreates the environment
- `run_tests.sh` - Runs the test suite
- `set_log_level.sh` - Sets the logging level

## Usage

Most scripts can be run without arguments:

```bash
./bin/initialize_db.sh
```

Some scripts accept parameters:

```bash
./bin/run_realistic_simulation.sh --start-date 2023-01-01 --end-date 2023-12-31
```

For more information on each script, run it with the `--help` flag:

```bash
./bin/run_realistic_simulation.sh --help
```