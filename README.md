# Australian Health Insurance Simulation

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![SQL Server](https://img.shields.io/badge/SQL%20Server-2019-red.svg)](https://www.microsoft.com/en-us/sql-server/sql-server-2019)

A realistic simulation of an Australian health insurance company's operational database, designed as a source for data warehouse demonstrations and testing. This project generates time-series data with daily changes that can be tracked using SQL Server's Change Data Capture (CDC).

## 📋 Features

- **Core Insurance Operations**
  - Member management and demographics
  - Policy creation and lifecycle management
  - Coverage plan configuration
  - Claims processing and assessment
  - Premium payment tracking
  - Provider network management
- **Data Generation**
  - Dynamic patient data generation with realistic demographics
  - Age distributions matching population demographics
  - Life stages with address and name changes over time
  - Data variants to simulate errors and changes
  - Enhanced data generation for fraud detection and financial analysis
  - Risk profiles and billing pattern detection
  - Actuarial metrics and financial transactions
- **Australian-Specific Elements**
  - Hospital cover tiers (Basic, Bronze, Silver, Gold)
  - Private Health Insurance (PHI) rebate tiers
  - Lifetime Health Cover (LHC) loading
  - Medicare Benefits Schedule (MBS) integration
  - Australian states and postcodes
- **Technical Features**
  - SQL Server Change Data Capture (CDC) for tracking changes
  - Synthea FHIR patient data integration
  - PyODBC database connectivity
  - Comprehensive test suite
  - Cross-platform support (Linux, macOS, Windows)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- SQL Server instance
- ODBC Driver 17+ for SQL Server
- pyodbc package
- Faker library (for dynamic data generation)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/health-insurance-au.git
cd health-insurance-au

# Install dependencies
pip install -e .
```

### Database Configuration

Create a configuration file with your database credentials:

```bash
cp config/db_config.env.example config/db_config.env
# Edit config/db_config.env with your database credentials
```

### Initialize the Database

#### On Linux/macOS:
```bash
# Initialize the database with standard schema
./bin/initialize_db.sh

# Initialize the database with enhanced schema for fraud detection and financial analysis
./bin/initialize_db.sh --include-enhanced

# Add initial reference data
./bin/add_initial_data.sh
```

#### On Windows:
```batch
# Initialize the database with standard schema
bin\initialize_db.bat

# Initialize the database with enhanced schema for fraud detection and financial analysis
bin\initialize_db.bat --include-enhanced

# Add initial reference data
bin\add_initial_data.bat
```

## 🏃‍♂️ Running Simulations

### Quick Start

Run a realistic simulation with dynamic data generation:

#### On Linux/macOS:
```bash
./bin/run_realistic_simulation.sh --start-date 2023-01-01 --end-date 2023-01-31 --members-per-day 10

# Run enhanced simulation with fraud detection and financial analysis
./bin/run_enhanced_simulation.sh --start-date 2023-01-01 --end-date 2023-01-31 --members-per-day 10
```

#### On Windows:
```batch
bin\run_realistic_simulation.bat --start-date 2023-01-01 --end-date 2023-01-31 --members-per-day 10

# Run enhanced simulation with fraud detection and financial analysis
bin\run_enhanced_simulation.bat --start-date 2023-01-01 --end-date 2023-01-31 --members-per-day 10
```

### Simulation Options

| Option | Description |
|--------|-------------|
| `--start-date` | Start date for the simulation (YYYY-MM-DD) |
| `--end-date` | End date for the simulation (YYYY-MM-DD) |
| `--members-per-day` | Base number of new members per day |
| `--log-level` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `--reset-members` | Reset the list of used member IDs |
| `--use-static-data` | Use static data from JSON file instead of dynamic generation |
| `--disable-enhanced` | Disable enhanced simulation features (for enhanced simulation only) |

### Enhanced Database Schema

The enhanced database schema adds additional capabilities for fraud detection, financial analysis, and actuarial metrics:

1. **Member Risk Profiles**: Extended attributes for risk scoring, chronic condition flags, and churn prediction
2. **Policy Risk Attributes**: APRA entity codes, risk-adjusted loading, and underwriting scores
3. **Fraud Detection**: Anomaly scores, fraud indicators, and pattern detection
4. **Provider Billing Analysis**: Billing pattern scores, claim frequency ratings, and compliance scores
5. **Financial Transactions**: Detailed tracking of all financial movements
6. **Actuarial Metrics**: Loss ratios, lapse rates, and acquisition costs by demographic segments

To enable these features, use the `--include-enhanced` flag when initializing the database:

```bash
./bin/initialize_db.sh --include-enhanced
```

### Data Generation

The simulation generates data with realistic patterns:

- Fewer members join on weekends
- More claims at the beginning/end of the month
- Business hours for transactions (8 AM to 5 PM)

#### Dynamic vs Static Data

By default, the simulation uses dynamic data generation to create realistic patient profiles:

#### On Linux/macOS:
```bash
# Use dynamic data generation (default)
./bin/run_realistic_simulation.sh --start-date 2023-01-01 --end-date 2023-01-31

# Use static data from JSON file
./bin/run_realistic_simulation.sh --start-date 2023-01-01 --end-date 2023-01-31 --use-static-data
```

#### On Windows:
```batch
# Use dynamic data generation (default)
bin\run_realistic_simulation.bat --start-date 2023-01-01 --end-date 2023-01-31

# Use static data from JSON file
bin\run_realistic_simulation.bat --start-date 2023-01-01 --end-date 2023-01-31 --use-static-data
```

## 📊 Database Structure

The database is organized into the following schemas:

### Insurance Schema

Core operational tables for the insurance business:

- **Members** - Personal information, contact details, Medicare numbers, risk profiles
- **CoveragePlans** - Plan details, benefits, premiums, waiting periods
- **Policies** - Policy details, status, coverage type, excess amounts, risk attributes
- **PolicyMembers** - Relationship between policies and members
- **Claims** - Claim details, status, payment information, fraud indicators
- **Providers** - Provider information, specialties, agreement status, billing patterns
- **PremiumPayments** - Payment tracking, due dates, payment status
- **FraudIndicators** - Reference data for fraud detection
- **FinancialTransactions** - Financial transaction records
- **ActuarialMetrics** - Reference data for actuarial analysis
- **ClaimPatterns** - Tracking of claim patterns

### Regulatory Schema

Tables related to Australian health insurance regulations:

- **PHIRebateTiers** - Private Health Insurance rebate tiers and rates
- **MBSItems** - Medicare Benefits Schedule items and rebates

### Integration Schema

Tables for Synthea FHIR data integration:

- **SyntheaPatients** - Patient data from Synthea
- **SyntheaEncounters** - Encounter data from Synthea
- **SyntheaProcedures** - Procedure data from Synthea

## 📈 Change Data Capture (CDC)

This project uses SQL Server's Change Data Capture (CDC) feature to track changes to the data over time.

### Enable CDC

#### On Linux/macOS:
```bash
# Enable CDC on the database and tables
./bin/enable_cdc.sh
```

#### On Windows:
```batch
# Enable CDC on the database and tables
bin\enable_cdc.bat
```

### Monitor CDC Changes

```bash
# Monitor changes to a specific table for the last 24 hours
./bin/monitor_cdc.sh --schema Insurance --table Members --hours 24
```

## 🧪 Testing

Run the test suite:

#### On Linux/macOS:
```bash
# Run all tests
./bin/run_tests.sh

# Run tests with coverage report
./bin/run_tests.sh coverage
```

#### On Windows:
```batch
# Run all tests
bin\run_tests.bat

# Run tests with coverage report
bin\run_tests.bat coverage
```

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- [Database Configuration](docs/database_configuration.md)
- [Change Data Capture](docs/change_data_capture.md)
- [Synthea Integration](docs/synthea_integration.md)
- [Dynamic Data Generation](docs/dynamic_data_generation.md)
- [Enhanced Simulation](docs/enhanced_simulation.md)

## 📁 Project Structure

```
health_insurance_au/          # Main Python package
├── api/                      # API endpoints
├── cli/                      # Command-line interfaces
├── models/                   # Data models
├── simulation/               # Simulation modules
│   └── simulation.py         # Core simulation logic
├── utils/                    # Utility functions
│   ├── data_generation/      # Dynamic patient data generation
│   │   └── generate_data.py  # Core data generation script
│   ├── data_loader.py        # Load data from static files
│   └── dynamic_data_generator.py  # Dynamic data integration
├── integration/              # External system integration
├── data_generation/          # Enhanced data generation
│   ├── fraud_patterns.py     # Fraud pattern generation
│   ├── financial_transactions.py # Financial transaction generation
│   ├── provider_billing.py   # Provider billing pattern generation
│   ├── claim_patterns.py     # Claim pattern generation
│   └── actuarial_data.py     # Actuarial data generation
└── config.py                 # Configuration settings

scripts/                      # Standalone scripts
├── db/                       # Database scripts
└── simulation/               # Simulation scripts
    ├── realistic_simulation.py  # Realistic simulation script
    └── enhanced_realistic_simulation.py  # Enhanced simulation script

bin/                          # Scripts for running operations
├── initialize_db.sh/.bat     # Database initialization
├── add_initial_data.sh/.bat  # Add initial data
├── run_realistic_simulation.sh/.bat  # Run realistic simulation
├── run_enhanced_simulation.sh/.bat   # Run enhanced simulation
├── enable_cdc.sh/.bat        # Enable CDC
└── run_tests.sh/.bat         # Run tests

config/                       # Configuration files
docs/                         # Documentation
data/                         # Data files
tests/                        # Test suite
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

Project Maintainer - Mehdi Modarressi

Project Link: [https://github.com/Mmodarre/AusHealthSim](https://github.com/Mmodarre/AusHealthSim)