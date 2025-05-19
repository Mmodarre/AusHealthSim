# Insurance Simulation Testing Framework

This directory contains the testing framework for the insurance simulation project. The framework includes unit tests, integration tests, and end-to-end tests to ensure the correctness and consistency of the simulation.

## Test Structure

The testing framework is organized as follows:

```
tests/
├── unit/                  # Unit tests for individual components
│   ├── models/            # Tests for data models
│   │   └── test_enhanced_models.py  # Tests for enhanced data models
│   ├── simulation/        # Tests for simulation modules
│   └── utils/             # Tests for utility functions
├── integration/           # Integration tests for component interactions
│   ├── test_db_integration.py        # Tests for database operations
│   ├── test_enhanced_schema.py       # Tests for enhanced database schema
│   ├── test_initialize_db_enhanced.py # Tests for database initialization with enhanced schema
│   ├── test_model_integration.py     # Tests for model interactions with database
│   ├── test_simulation_integration.py # Tests for simulation components
│   ├── test_cdc_integration.py       # Tests for CDC functionality
│   └── test_synthea_integration.py   # Tests for Synthea FHIR integration
├── test_date_consistency_e2e.py      # End-to-end test for date consistency
├── test_enhanced_simulation.py       # Tests for enhanced simulation features
├── conftest.py                       # Pytest configuration and fixtures
└── run_tests.py                      # Script to run all tests
```

## Test Types

### Unit Tests

Unit tests focus on testing individual components in isolation, using mocks and stubs to avoid external dependencies. These tests verify the correctness of:

- Data models and their methods
- Utility functions
- Simulation logic
- Database utility functions (mocked)
- Enhanced data models and their methods

### Integration Tests

Integration tests verify the interaction between different components of the system, including:

- Database operations with the actual database
- Model interactions with the database
- Simulation components working together
- CDC (Change Data Capture) functionality
- Synthea FHIR data integration
- Enhanced database schema and operations
- Database initialization with enhanced schema

### End-to-End Tests

End-to-end tests validate the entire system working together, simulating real-world scenarios:

- Running a complete daily simulation
- Verifying date consistency across all generated data
- Testing the full workflow from data generation to database storage
- Testing enhanced simulation features

## Date Consistency Testing

A key focus of the testing framework is ensuring date consistency throughout the simulation. The simulation date should be used consistently for all generated data, with the only exception being the next premium payment date (which is calculated based on the policy start date and payment frequency).

The date consistency tests verify that:

1. All claim numbers include the simulation date
2. All service dates are before or on the simulation date
3. All submission dates are between the service date and the simulation date
4. All processed dates and payment dates are on or before the simulation date
5. All LastModified dates match the simulation date
6. All provider agreement dates are relative to the simulation date
7. All policy dates (except next premium due date) are relative to the simulation date

## Enhanced Simulation Testing

The enhanced simulation tests verify the functionality of the enhanced features, including:

1. **Enhanced Data Models**: Testing the extended attributes of Member, Policy, Claim, and Provider models
2. **New Data Models**: Testing the new FraudIndicator, FinancialTransaction, ActuarialMetric, and ClaimPattern models
3. **Enhanced Database Schema**: Testing the extended tables and columns in the database
4. **Data Generation Modules**: Testing the fraud pattern, financial transaction, provider billing, claim pattern, and actuarial data generation modules
5. **Simulation Orchestration**: Testing the coordination of all enhanced features

## Running the Tests

### Using run_tests.py

The `run_tests.py` script provides a convenient way to run different types of tests:

```bash
# Run all tests (unit, integration, and e2e)
python tests/run_tests.py

# Run only unit tests
python tests/run_tests.py --unit

# Run only integration tests
python tests/run_tests.py --integration

# Run only end-to-end tests
python tests/run_tests.py --e2e --date 2022-10-22

# Run only enhanced simulation tests
python tests/run_tests.py --enhanced
```

### Using pytest directly

You can also use pytest directly:

```bash
# Run all unit tests
pytest tests/unit

# Run all integration tests
pytest tests/integration

# Run a specific test file
pytest tests/integration/test_db_integration.py

# Run a specific test function
pytest tests/integration/test_db_integration.py::TestDatabaseIntegration::test_connection

# Run enhanced simulation tests
pytest tests/test_enhanced_simulation.py

# Run enhanced model tests
pytest tests/unit/models/test_enhanced_models.py
```

## Test Coverage

The testing framework aims to provide comprehensive coverage of the codebase, with particular focus on:

1. Date handling across all components
2. Database operations
3. Data generation for all entity types
4. Simulation flow and control
5. CDC functionality
6. Synthea FHIR integration
7. Enhanced simulation features
8. Enhanced database schema

## Testing Enhanced Features

When testing enhanced features, you need to initialize the database with the enhanced schema:

```bash
# Initialize database with enhanced schema
./bin/initialize_db.sh --include-enhanced

# Run enhanced simulation
./bin/run_enhanced_simulation.sh --start-date 2023-01-01 --end-date 2023-01-31
```

Some tests for enhanced features will be skipped if the database is not initialized with the enhanced schema. You can check if the enhanced schema is available by running:

```bash
python -c "from health_insurance_au.utils.db_utils import execute_query; print(execute_query('SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = \'FraudIndicators\' AND TABLE_SCHEMA = \'Insurance\''))"
```

## Continuous Integration

These tests can be integrated into a CI/CD pipeline to ensure that changes to the codebase do not break existing functionality or introduce date inconsistencies.