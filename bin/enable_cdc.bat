@echo off
REM Script to enable CDC on the Health Insurance AU database

REM Get the directory of this script
SET "SCRIPT_DIR=%~dp0"
SET "PROJECT_ROOT=%SCRIPT_DIR%.."

REM Default values
SET "ENV_FILE=%PROJECT_ROOT%\config\db_config.env"

REM Parse command line arguments
:parse_args
IF "%~1"=="" GOTO end_parse_args
IF "%~1"=="--env-file" (
    SET "ENV_FILE=%~2"
    SHIFT
    GOTO next_arg
)
ECHO Unknown option: %~1
ECHO Usage: %0 [--env-file FILE]
EXIT /B 1

:next_arg
SHIFT
GOTO parse_args

:end_parse_args

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

REM Set environment variables for Python
SET "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

REM Run the Python script to enable CDC
ECHO Enabling CDC using environment file: %ENV_FILE%...
python "%PROJECT_ROOT%\scripts\db\enable_cdc.py" --env-file "%ENV_FILE%"

ECHO CDC setup completed.