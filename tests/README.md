# Insurance Simulation Testing Framework

This directory contains the testing framework for the insurance simulation project. The framework includes unit tests, integration tests, and end-to-end tests to ensure the correctness and consistency of the simulation.

## Test Structure

The testing framework is organized as follows:

```
tests/
├── unit/                  # Unit tests for individual components
│   ├── models/            # Tests for data models
│   ├── simulation/        # Tests for simulation modules
│   └── utils/             # Tests for utility functions
├── integration/           # Integration tests for component interactions
│   ├── test_db_integration.py        # Tests for database operations
│   ├── test_model_integration.py     # Tests for model interactions with database
│   ├── test_simulation_integration.py # Tests for simulation components
│   ├── test_cdc_integration.py       # Tests for CDC functionality
│   └── test_synthea_integration.py   # Tests for Synthea FHIR integration
├── test_date_consistency_e2e.py      # End-to-end test for date consistency
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

### Integration Tests

Integration tests verify the interaction between different components of the system, including:

- Database operations with the actual database
- Model interactions with the database
- Simulation components working together
- CDC (Change Data Capture) functionality
- Synthea FHIR data integration

### End-to-End Tests

End-to-end tests validate the entire system working together, simulating real-world scenarios:

- Running a complete daily simulation
- Verifying date consistency across all generated data
- Testing the full workflow from data generation to database storage

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
```

## Test Coverage

The testing framework aims to provide comprehensive coverage of the codebase, with particular focus on:

1. Date handling across all components
2. Database operations
3. Data generation for all entity types
4. Simulation flow and control
5. CDC functionality
6. Synthea FHIR integration

## Continuous Integration

These tests can be integrated into a CI/CD pipeline to ensure that changes to the codebase do not break existing functionality or introduce date inconsistencies.