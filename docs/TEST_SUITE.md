# Health Insurance Simulation Test Suite

This document provides an overview of the test suite for the Health Insurance Simulation project.

## Test Structure

The test suite is organized into two main categories:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test components working together with the database

```
tests/
├── conftest.py           # Shared test fixtures
├── unit/                 # Unit tests
│   ├── test_models.py    # Test data models
│   ├── test_db_utils.py  # Test database utilities
│   ├── test_claims.py    # Test claims generation
│   ├── test_cdc_utils.py # Test CDC utilities
│   ├── test_synthea.py   # Test Synthea integration
│   ├── test_simulation.py # Test simulation module
│   └── test_data_loader.py # Test data loading
└── integration/
    └── test_db_integration.py # Test database operations
```

## Running Tests

Use the provided `run_tests.sh` script to run the tests:

```bash
# Run unit tests only (default)
./run_tests.sh

# Run integration tests only
./run_tests.sh integration

# Run all tests
./run_tests.sh all

# Run with coverage report
./run_tests.sh coverage
```

## Implementation Status

The following tests have been implemented and are passing:

### Working Tests
- **test_models.py**: All tests passing (100% coverage of models.py)
- **test_claims.py**: All tests passing (90% coverage of claims.py)
- **test_data_loader.py**: All tests passing (83% coverage of data_loader.py)

### Tests Requiring Additional Work
- **test_db_utils.py**: Most tests passing but has issues with mocking pyodbc
- **test_cdc_utils.py**: Needs fixes for mocking database interactions
- **test_synthea.py**: Needs fixes for mocking database interactions
- **test_simulation.py**: Needs fixes for mocking database interactions
- **test_db_integration.py**: Requires actual database connection

## Unit Tests

### Models (test_models.py)

Tests for the data model classes:
- Member
- CoveragePlan
- Policy
- PolicyMember
- Provider
- Claim
- PremiumPayment

These tests verify that model objects correctly convert to dictionaries for database operations.

### Database Utilities (test_db_utils.py)

Tests for database utility functions:
- get_connection
- execute_query
- execute_non_query
- execute_stored_procedure
- bulk_insert

These tests use mocks to isolate the database functions from actual database connections.

### Claims Generation (test_claims.py)

Tests for the claims generation functionality:
- generate_claim_number
- generate_hospital_claims
- generate_general_treatment_claims

These tests verify that claims are generated with correct properties, financial calculations, and status transitions.

### CDC Utilities (test_cdc_utils.py)

Tests for the Change Data Capture utilities:
- list_cdc_tables
- get_cdc_changes
- get_cdc_net_changes

These tests verify that CDC changes are correctly retrieved and processed.

### Synthea Integration (test_synthea.py)

Tests for the Synthea FHIR integration:
- process_patient
- process_encounter
- process_procedure
- link_patient_to_member
- generate_claim_from_encounter

These tests verify that FHIR resources are correctly processed and integrated with the insurance system.

### Simulation (test_simulation.py)

Tests for the main simulation module:
- run_daily_simulation
- run_historical_simulation

These tests verify that the simulation correctly orchestrates all components and handles different simulation frequencies.

### Data Loader (test_data_loader.py)

Tests for the data loading utilities:
- load_sample_data
- load_members_from_json
- load_providers
- load_coverage_plans

These tests verify that sample data is correctly loaded from JSON files and generated for testing.

## Integration Tests

### Database Integration (test_db_integration.py)

Tests that interact with an actual database:
- test_connection
- test_execute_query
- test_execute_non_query
- test_bulk_insert
- test_member_model_integration

These tests require a connection to the actual database and are skipped by default unless the `TEST_DB` environment variable is set to `true`.

## Test Coverage

The test suite aims to cover:

1. **Core Functionality**: All main features of the system
2. **Edge Cases**: Handling of unusual or boundary conditions
3. **Error Handling**: Proper handling of errors and exceptions
4. **Integration Points**: Correct interaction between components

## Test Dependencies

The testing framework uses:
- pytest: Testing framework
- pytest-cov: Coverage reporting
- pytest-mock: Mocking functionality

Install test dependencies with:

```bash
pip install -r requirements-dev.txt
```

## Best Practices

The test suite follows these best practices:

1. **Isolation**: Tests do not depend on each other
2. **Mocking**: External dependencies are mocked for unit tests
3. **Fixtures**: Common test data is provided through fixtures
4. **Clear Assertions**: Test assertions clearly indicate what is being verified
5. **Coverage**: Tests aim for high code coverage
6. **Readability**: Test names and structures are clear and descriptive