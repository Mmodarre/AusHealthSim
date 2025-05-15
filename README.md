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
- Dynamic patient data generation with realistic demographics
- Supports integration with Synthea synthetic patient data
- Uses SQL Server Change Data Capture (CDC) for change tracking
- Configurable simulation parameters

## Project Structure

The project is organized into the following directories:

- `health_insurance_au/` - Main Python package
  - `api/` - API endpoints (if needed)
  - `cli/` - Command-line interfaces
  - `core/` - Core business logic and constants
  - `db/` - Database-specific code
  - `integration/` - Integration with external systems
  - `models/` - Data models
  - `simulation/` - Simulation modules
  - `utils/` - Utility functions
    - `data_generation/` - Dynamic patient data generation
    - `data_loader.py` - Load data from static files
    - `dynamic_data_generator.py` - Generate data dynamically
- `scripts/` - Standalone Python scripts
  - `db/` - Database-related scripts
  - `simulation/` - Simulation-related scripts
  - `utils/` - Utility scripts
- `bin/` - Shell scripts for running operations
- `config/` - Configuration files
- `data/` - Data files
- `docs/` - Documentation
- `logs/` - Log files
- `reports/` - Generated reports
- `tests/` - Test suite
  - `unit/` - Unit tests
  - `integration/` - Integration tests

## Documentation

Detailed documentation is available in the `docs/` directory:

- [Database Configuration](docs/database_configuration.md) - Setting up and configuring database connections
- [Change Data Capture](docs/change_data_capture.md) - Working with CDC for change tracking
- [Synthea Integration](docs/synthea_integration.md) - Integrating with Synthea synthetic patient data
- [Dynamic Data Generation](docs/dynamic_data_generation.md) - Generating realistic patient data dynamically

## Getting Started

### Prerequisites

- Python 3.8+
- SQL Server instance
- ODBC Driver 17 for SQL Server
- pyodbc package
- Faker library (for dynamic data generation)

### Installation

#### Using pip

```bash
# Install from the current directory
pip install -e .
```

#### Manual Setup

1. Clone this repository
2. Set up your database configuration (see below)
3. Run the initialization script:
   ```bash
   ./bin/initialize_db.sh
   ```
4. Add initial data:
   ```bash
   ./bin/add_initial_data.sh
   ```

### Database Configuration

The project uses multiple methods for configuring database connections, with the following order of precedence:

1. Command-line arguments (highest precedence)
2. Environment variables
3. Configuration file (`config/db_config.env`)
4. Default values (lowest precedence)

#### Using a Configuration File

Copy the example configuration file and edit it with your database credentials:

```bash
cp config/db_config.env.example config/db_config.env
# Edit config/db_config.env with your database credentials
```

#### Using Environment Variables

You can set the following environment variables:

```bash
export DB_SERVER=your_server_address
export DB_DATABASE=your_database_name
export DB_USERNAME=your_username
export DB_PASSWORD=your_password
export DB_DRIVER="{ODBC Driver 17 for SQL Server}"
```

## Usage

### Command-Line Tools

After installation, you can use the following command-line tools:

```bash
# Initialize the database
hi-init-db

# Add initial data
hi-add-data

# Enable CDC
hi-enable-cdc

# Run a simulation
hi-simulation
```

### Shell Scripts

Alternatively, you can use the shell scripts in the `bin/` directory:

```bash
# Initialize the database
./bin/initialize_db.sh

# Add initial data
./bin/add_initial_data.sh

# Run a complete simulation
./bin/run_complete_simulation.sh
```

### Running a Realistic Simulation

To run a realistic simulation with dynamic data generation:

```bash
# Run a simulation from January 1, 2023 to January 31, 2023 with 10 new members per day
./bin/run_realistic_simulation.sh --start-date 2023-01-01 --end-date 2023-01-31 --members-per-day 10

# Use static data from JSON file instead of dynamic generation
./bin/run_realistic_simulation.sh --start-date 2023-01-01 --end-date 2023-01-31 --use-static-data
```

The simulation will generate realistic data with daily patterns (fewer members on weekends, more claims at the beginning/end of month, etc.).

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

## Simulation Parameters

The simulation can be customized with various parameters. See `config/simulation.conf` for available options, or run:

```bash
hi-simulation --help
```

### Dynamic Data Generation

The simulation can generate patient data dynamically using the Faker library, which creates realistic demographics with:

- Age distributions matching population demographics
- Realistic names, addresses, and contact information
- Life stages with address and name changes over time
- Variants to simulate data entry errors or name changes
- Australian state and postcode information

To use dynamic data generation (default behavior):

```bash
./bin/run_realistic_simulation.sh --start-date 2023-01-01 --end-date 2023-01-31
```

To use static data from the JSON file instead:

```bash
./bin/run_realistic_simulation.sh --start-date 2023-01-01 --end-date 2023-01-31 --use-static-data
```

## Australian Health Insurance Specifics

The simulation includes Australian-specific health insurance features:

- Hospital cover tiers (Basic, Bronze, Silver, Gold)
- Private Health Insurance (PHI) rebate tiers
- Lifetime Health Cover (LHC) loading
- Medicare Benefits Schedule (MBS) items
- Australian states and postcodes
- Waiting periods for pre-existing conditions

## Change Data Capture (CDC)

This project uses SQL Server's Change Data Capture (CDC) feature to track changes to the data.

### CDC Setup

To enable CDC on the database:

```bash
hi-enable-cdc
```

or use the shell script:

```bash
./bin/enable_cdc.sh
```

### Monitoring CDC Changes

To monitor CDC changes:

```bash
hi-monitor-cdc --schema Insurance --table Members --hours 24
```

## Testing

The project includes a comprehensive test suite to ensure code quality and reliability.

### Running Tests

To run the tests, use the provided script:

```bash
# Run all tests
./bin/run_tests.sh

# Run tests with coverage report
./bin/run_tests.sh coverage
```

Or use pytest directly:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=health_insurance_au
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.