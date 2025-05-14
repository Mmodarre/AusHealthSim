# Australian Health Insurance Simulation

This project simulates an Australian health insurance company's operational database, designed to be used as a source for data warehouse demonstrations. The simulation generates realistic data with daily changes that can be tracked over time.

## Features

- Simulates core health insurance operations including:
  - Member management
  - Policy creation and updates
  - Coverage plan management
  - Claims processing
  - Premium payments
  - Provider management
- Generates realistic Australian health insurance data
- Supports integration with Synthea synthetic patient data
- Uses SQL Server Change Data Capture (CDC) for change tracking
- Configurable simulation parameters

## Documentation

Detailed documentation is available in the `docs/` directory:

- [Database Configuration](docs/database_configuration.md) - Setting up and configuring database connections
- [Change Data Capture](docs/change_data_capture.md) - Working with CDC for change tracking
- [Synthea Integration](docs/synthea_integration.md) - Integrating with Synthea synthetic patient data

## Getting Started

### Prerequisites

- Python 3.8+
- SQL Server instance
- ODBC Driver 17 for SQL Server
- pyodbc package

### Database Configuration

The project uses environment variables or a configuration file to store database credentials. This approach avoids hardcoding sensitive information in the code.

#### Configuration Methods (in order of precedence)

1. Command-line arguments (highest precedence)
2. Environment variables
3. Configuration file (db_config.env)
4. Default values (lowest precedence)

#### Environment Variables

You can set the following environment variables:

```bash
export DB_SERVER=your_server_address
export DB_DATABASE=your_database_name
export DB_USERNAME=your_username
export DB_PASSWORD=your_password
export DB_DRIVER="{ODBC Driver 17 for SQL Server}"
```

#### Configuration File

Alternatively, create a file named `db_config.env` in the `health_insurance_au` directory with the following content:

```
DB_SERVER=your_server_address
DB_DATABASE=your_database_name
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_DRIVER={ODBC Driver 17 for SQL Server}
```

A template file `db_config.env.example` is provided for reference.

#### Command-line Arguments

All scripts accept command-line arguments to override the database configuration:

```bash
python initialize_db.py --server your_server_address --username your_username --password your_password --database your_database_name
```

You can also specify a custom environment file:

```bash
python initialize_db.py --env-file /path/to/your/env/file
```

#### Security Notes

- The `db_config.env` file is included in `.gitignore` to prevent accidentally committing credentials
- For production environments, consider using a secure vault or key management service

### Installation

1. Clone this repository
2. Set up your database configuration using one of the methods above
3. Run the initialization script to set up the database:
   ```
   python initialize_db.py
   ```
   or use the shell script wrapper:
   ```
   ./initialize_db.sh
   ```
4. Add initial data to the database:
   ```
   python add_initial_data.py
   ```
   or use the shell script wrapper:
   ```
   ./add_initial_data.sh
   ```

## Database Structure

The database is organized into the following schemas:

- **Insurance**: Core operational tables
  - Members
  - CoveragePlans
  - Policies
  - PolicyMembers
  - Claims
  - Providers
  - PremiumPayments
- **Regulatory**: Australian health insurance regulations
  - PHIRebateTiers
  - MBSItems
- **Simulation**: Stored procedures for data simulation
- **Integration**: Tables for Synthea FHIR data integration
  - SyntheaPatients
  - SyntheaEncounters
  - SyntheaProcedures

## Usage

### Run a complete simulation

```bash
./run_complete_simulation.sh
```

This script will:
1. Initialize the database (with the `--drop` option to start fresh)
2. Add initial data (50 members, 15 coverage plans, 30 providers)
3. Run a historical simulation from January 1, 2023 to December 31, 2023 with weekly frequency

### Individual Commands

1. Initialize the database:
   ```bash
   python initialize_db.py
   ```

2. Add initial data:
   ```bash
   python add_initial_data.py
   ```

3. Enable CDC (Change Data Capture):
   ```bash
   python enable_cdc.py
   ```

## Simulation Parameters

The simulation can be customized with various parameters:

- **Daily Simulation**:
  - `--date`: Simulation date (default: today)
  - `--members`: Number of new members to add
  - `--plans`: Number of new plans to add
  - `--policies`: Number of new policies to create
  - `--hospital-claims`: Number of hospital claims to generate
  - `--general-claims`: Number of general claims to generate
  - Various flags to skip specific operations

- **Historical Simulation**:
  - `--start-date`: Start date for the simulation
  - `--end-date`: End date for the simulation (default: today)
  - `--frequency`: Simulation frequency (daily, weekly, monthly)

- **Synthea Integration**:
  - `--dir`: Directory containing Synthea FHIR JSON files
  - `--patients`: Limit on number of patients to import
  - `--encounters`: Limit on number of encounters to import
  - `--procedures`: Limit on number of procedures to import
  - `--claims`: Limit on number of claims to generate
  - Various flags to skip specific operations

## Australian Health Insurance Specifics

The simulation includes Australian-specific health insurance features:

- Hospital cover tiers (Basic, Bronze, Silver, Gold)
- Private Health Insurance (PHI) rebate tiers
- Lifetime Health Cover (LHC) loading
- Medicare Benefits Schedule (MBS) items
- Australian states and postcodes
- Waiting periods for pre-existing conditions

## Change Data Capture (CDC)

This project uses SQL Server's Change Data Capture (CDC) feature to track changes to the data. CDC captures insert, update, and delete operations applied to SQL Server tables, making the details of the changes available in relational tables.

### CDC Setup

To enable CDC on the database:

```bash
python enable_cdc.py
```
or use the shell script wrapper:
```bash
./enable_cdc.sh
```

This script will:
1. Enable CDC on the database
2. Enable CDC on all relevant tables

### Monitoring CDC Changes

To monitor CDC changes:

```bash
./monitor_cdc.sh --schema Insurance --table Members --hours 24
```

Options:
- `--schema`: Schema name (default: Insurance)
- `--table`: Table name (default: Members)
- `--hours`: Number of hours to look back (default: 24)
- `--list-tables`: List all tables with CDC enabled
- `--net-changes`: Show only net changes (final state of each row)

## Data Warehouse Considerations

This operational database is designed to be a good source for data warehouse demonstrations:

- Change Data Capture (CDC) tracks all data modifications
- Daily operations create realistic data patterns
- Multiple related entities for dimensional modeling
- Integration with external data sources (Synthea)
- Australian-specific business rules and regulations

## Testing

The project includes a comprehensive test suite to ensure code quality and reliability.

### Running Tests

To run the tests, use the provided `run_tests.sh` script:

```bash
# Run unit tests (default)
./run_tests.sh

# Run integration tests only
./run_tests.sh integration

# Run all tests (unit and integration)
./run_tests.sh all

# Run tests with coverage report
./run_tests.sh coverage
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
  - Models
  - Database utilities
  - Claims generation
  - CDC utilities
  - Synthea integration

- **Integration Tests**: Test components working together
  - Database operations
  - End-to-end workflows

### Test Dependencies

The testing framework uses:
- pytest: Testing framework
- pytest-cov: Coverage reporting
- pytest-mock: Mocking functionality

Install test dependencies with:

```bash
pip install -r requirements-dev.txt
```

### Integration Test Configuration

Integration tests require a connection to the actual database. These tests are skipped by default unless the `TEST_DB` environment variable is set to `true`:

```bash
export TEST_DB=true
python -m pytest tests/integration
```