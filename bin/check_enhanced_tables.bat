@echo off
REM Check if data is being generated in the enhanced tables

REM Get the directory of this script
SET "SCRIPT_DIR=%~dp0"
SET "PROJECT_ROOT=%SCRIPT_DIR%.."

REM Set environment variables for Python
SET "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

REM Run the Python script
ECHO Checking enhanced tables...
python "%PROJECT_ROOT%\scripts\simulation\check_enhanced_tables.py"