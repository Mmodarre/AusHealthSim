@echo off
REM Wrapper script for the Realistic Health Insurance Simulation

REM Get the directory of this script
SET "SCRIPT_DIR=%~dp0"
SET "PROJECT_ROOT=%SCRIPT_DIR%.."

REM Default environment file
SET "ENV_FILE=%PROJECT_ROOT%\config\db_config.env"

REM Default values
SET "START_DATE="
SET "END_DATE="
SET "MEMBERS_PER_DAY=10"
SET "LOG_LEVEL=INFO"
SET "RESET_MEMBERS="
SET "USE_STATIC_DATA="

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
IF "%~1"=="--members-per-day" (
    SET "MEMBERS_PER_DAY=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--log-level" (
    SET "LOG_LEVEL=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--env-file" (
    SET "ENV_FILE=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--reset-members" (
    SET "RESET_MEMBERS=--reset-members"
    GOTO next_arg
)
IF "%~1"=="--use-static-data" (
    SET "USE_STATIC_DATA=--use-static-data"
    GOTO next_arg
)
ECHO Unknown option: %~1
ECHO Usage: %0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--members-per-day N] [--log-level LEVEL] [--env-file FILE] [--reset-members] [--use-static-data]
EXIT /B 1

:next_arg
SHIFT
GOTO parse_args

:end_parse_args

REM Validate required arguments
IF "%START_DATE%"=="" (
    ECHO Error: start-date is required
    ECHO Usage: %0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--members-per-day N] [--log-level LEVEL] [--env-file FILE] [--reset-members] [--use-static-data]
    EXIT /B 1
)

IF "%END_DATE%"=="" (
    ECHO Error: end-date is required
    ECHO Usage: %0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--members-per-day N] [--log-level LEVEL] [--env-file FILE] [--reset-members] [--use-static-data]
    EXIT /B 1
)

REM Check if the environment file exists
IF NOT EXIST "%ENV_FILE%" (
    ECHO Warning: Environment file %ENV_FILE% does not exist
    ECHO Using default database connection settings
) ELSE (
    REM Load environment variables from the config file
    FOR /F "tokens=1,2 delims==" %%G IN (%ENV_FILE%) DO (
        SET "%%G=%%H"
    )
)

REM Create logs directory if it doesn't exist
IF NOT EXIST "%PROJECT_ROOT%\logs" (
    ECHO Creating logs directory
    MKDIR "%PROJECT_ROOT%\logs"
)

REM Set environment variables for Python
SET "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"
SET "HEALTH_INSURANCE_LOG_DIR=%PROJECT_ROOT%\logs"

REM Run the Python script
ECHO Running realistic simulation from %START_DATE% to %END_DATE% with %MEMBERS_PER_DAY% members per day...
python "%PROJECT_ROOT%\scripts\simulation\realistic_simulation.py" ^
    --start-date "%START_DATE%" ^
    --end-date "%END_DATE%" ^
    --members-per-day "%MEMBERS_PER_DAY%" ^
    --log-level "%LOG_LEVEL%" ^
    %RESET_MEMBERS% ^
    %USE_STATIC_DATA%

ECHO Simulation completed!