@echo off
REM Test the financial transaction generator

REM Get the directory of this script
SET "SCRIPT_DIR=%~dp0"
SET "PROJECT_ROOT=%SCRIPT_DIR%.."

REM Set environment variables for Python
SET "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

REM Run the Python script
ECHO Testing financial transaction generator...
python "%PROJECT_ROOT%\scripts\simulation\test_financial_transactions.py"