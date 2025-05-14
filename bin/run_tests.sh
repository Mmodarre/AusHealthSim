#!/bin/bash

# Run unit tests only (default)
if [ "$1" == "" ] || [ "$1" == "unit" ]; then
    echo "Running unit tests..."
    python3 -m pytest tests/unit
fi

# Run integration tests only
if [ "$1" == "integration" ]; then
    echo "Running integration tests..."
    export TEST_DB=true
    python3 -m pytest tests/integration
fi

# Run all tests
if [ "$1" == "all" ]; then
    echo "Running all tests..."
    export TEST_DB=true
    python3 -m pytest
fi

# Run with coverage report
if [ "$1" == "coverage" ]; then
    echo "Running tests with coverage..."
    python3 -m pytest --cov=health_insurance_au --cov-report=html
    echo "Coverage report generated in htmlcov directory"
fi