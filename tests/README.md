# Insurance Simulation Testing Framework

This directory contains the testing framework for the insurance simulation project. The framework includes unit tests, integration tests, and end-to-end tests to ensure the correctness and consistency of the simulation.

## Test Structure

The testing framework is organized as follows:

```
tests/
├── unit/                  # Unit tests for individual components
│   ├── test_claims.py     # Tests for claims generation
│   ├── test_db_utils.py   # Tests for database utilities
│   ├── test_models.py     # Tests for data models
│   ├── test_simulation.py # Tests for the simulation engine
│   └── test_date_consistency.py # Tests for date consistency
├── integration/           # Integration tests for component interactions
│   ├── test_db_integration.py   # Tests for database integration
│   └── test_date_consistency_integration.py # Tests for date consistency across components
└── conftest.py            # Pytest configuration and fixtures

scripts/
└── testing/               # Testing scripts
    ├── test_date_consistency_e2e.py # End-to-end test for date consistency
    └── run_tests.py       # Script to run all tests
```

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

### Unit Tests

To run all unit tests:

```bash
pytest tests/unit
```

To run specific unit tests:

```bash
pytest tests/unit/test_date_consistency.py
```

### Integration Tests

To run all integration tests:

```bash
pytest tests/integration
```

### End-to-End Tests

The end-to-end tests require a connection to the database. To run the end-to-end tests:

```bash
python scripts/testing/test_date_consistency_e2e.py --date 2022-10-22
```

### Running All Tests

To run all tests (unit and integration):

```bash
python scripts/testing/run_tests.py
```

To include end-to-end tests:

```bash
python scripts/testing/run_tests.py --e2e --date 2022-10-22
```

## Test Coverage

The testing framework aims to provide comprehensive coverage of the codebase, with particular focus on:

1. Date handling across all components
2. Database operations
3. Data generation for all entity types
4. Simulation flow and control

## Continuous Integration

These tests can be integrated into a CI/CD pipeline to ensure that changes to the codebase do not break existing functionality or introduce date inconsistencies.