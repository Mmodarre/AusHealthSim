@echo off
REM Run a historical simulation with enhanced features enabled

REM Get the directory of this script
SET "SCRIPT_DIR=%~dp0"
SET "PROJECT_ROOT=%SCRIPT_DIR%.."

REM Default values
SET "START_DATE="
SET "END_DATE="
SET "FREQUENCY=daily"
SET "USE_DYNAMIC_DATA="

REM Parse command line arguments
:parse_args
IF "%~1"=="" GOTO end_parse_args
IF "%~1"=="--start-date" (
    SET "START_DATE=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--end-date" (
    SET "END_DATE=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--frequency" (
    SET "FREQUENCY=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--use-dynamic-data" (
    SET "USE_DYNAMIC_DATA=--use-dynamic-data"
    GOTO next_arg
)
ECHO Unknown option: %~1
ECHO Usage: %0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--frequency daily|weekly|monthly] [--use-dynamic-data]
EXIT /B 1

:next_arg
SHIFT
GOTO parse_args

:end_parse_args

REM Validate required arguments
IF "%START_DATE%"=="" (
    ECHO Error: start-date is required
    ECHO Usage: %0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--frequency daily|weekly|monthly] [--use-dynamic-data]
    EXIT /B 1
)

IF "%END_DATE%"=="" (
    ECHO Error: end-date is required
    ECHO Usage: %0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--frequency daily|weekly|monthly] [--use-dynamic-data]
    EXIT /B 1
)

REM Set environment variables for Python
SET "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

REM Run the Python script
ECHO Running historical simulation from %START_DATE% to %END_DATE% with enhanced features...
python "%PROJECT_ROOT%\scripts\simulation\run_enhanced_historical.py" ^
    --start-date "%START_DATE%" ^
    --end-date "%END_DATE%" ^
    --frequency "%FREQUENCY%" ^
    %USE_DYNAMIC_DATA%

ECHO Simulation completed!