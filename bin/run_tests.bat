@echo off
REM Run tests for the Health Insurance AU project

REM Get the directory of this script
SET "SCRIPT_DIR=%~dp0"
SET "PROJECT_ROOT=%SCRIPT_DIR%.."

REM Set environment variables for Python
SET "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

REM Run unit tests only (default)
IF "%1"=="" GOTO run_unit
IF "%1"=="unit" GOTO run_unit

REM Run integration tests only
IF "%1"=="integration" GOTO run_integration

REM Run all tests
IF "%1"=="all" GOTO run_all

REM Run with coverage report
IF "%1"=="coverage" GOTO run_coverage

ECHO Unknown option: %1
ECHO Usage: %0 [unit|integration|all|coverage]
EXIT /B 1

:run_unit
ECHO Running unit tests...
python -m pytest tests\unit
GOTO end

:run_integration
ECHO Running integration tests...
SET "TEST_DB=true"
python -m pytest tests\integration
GOTO end

:run_all
ECHO Running all tests...
SET "TEST_DB=true"
python -m pytest
GOTO end

:run_coverage
ECHO Running tests with coverage...
python -m pytest --cov=health_insurance_au --cov-report=html
ECHO Coverage report generated in htmlcov directory
GOTO end

:end