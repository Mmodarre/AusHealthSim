@echo off
REM Add initial data to the Health Insurance AU database

REM Get the directory of this script
SET "SCRIPT_DIR=%~dp0"
SET "PROJECT_ROOT=%SCRIPT_DIR%.."
SET "ABSOLUTE_PROJECT_ROOT=%~f0\..\.."

REM Default values
SET "SERVER="
SET "USERNAME="
SET "PASSWORD="
SET "DATABASE="
SET "MEMBERS=50"
SET "PLANS=15"
SET "PROVIDERS=30"
SET "ENV_FILE=%PROJECT_ROOT%\config\db_config.env"

REM Parse command line arguments
:parse_args
IF "%~1"=="" GOTO end_parse_args
IF "%~1"=="--server" (
    SET "SERVER=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--username" (
    SET "USERNAME=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--password" (
    SET "PASSWORD=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--database" (
    SET "DATABASE=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--env-file" (
    SET "ENV_FILE=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--members" (
    SET "MEMBERS=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--plans" (
    SET "PLANS=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="--providers" (
    SET "PROVIDERS=%~2"
    SHIFT
    GOTO next_arg
)
IF "%~1"=="-h" GOTO show_help
IF "%~1"=="--help" GOTO show_help

ECHO Unknown option: %~1
ECHO Use --help to see available options.
EXIT /B 1

:next_arg
SHIFT
GOTO parse_args

:show_help
ECHO Usage: %0 [options]
ECHO.
ECHO Options:
ECHO   --server      SQL Server hostname or IP
ECHO   --username    SQL Server username
ECHO   --password    SQL Server password
ECHO   --database    Database name
ECHO   --env-file    Path to environment file (default: %ENV_FILE%)
ECHO   --members     Number of members to add (default: %MEMBERS%)
ECHO   --plans       Number of plans to add (default: %PLANS%)
ECHO   --providers   Number of providers to add (default: %PROVIDERS%)
ECHO   -h, --help    Show this help message and exit
EXIT /B 0

:end_parse_args

REM Set environment variables directly from config file if not provided as arguments
IF "%SERVER%"=="" IF "%USERNAME%"=="" IF "%PASSWORD%"=="" IF "%DATABASE%"=="" (
    ECHO Loading database configuration from %ENV_FILE%
    IF EXIST "%ENV_FILE%" (
        FOR /F "tokens=1,2 delims==" %%G IN (%ENV_FILE%) DO (
            IF "%%G"=="DB_SERVER" SET "SERVER=%%H"
            IF "%%G"=="DB_USERNAME" SET "USERNAME=%%H"
            IF "%%G"=="DB_PASSWORD" SET "PASSWORD=%%H"
            IF "%%G"=="DB_DATABASE" SET "DATABASE=%%H"
        )
    ) ELSE (
        ECHO WARNING: Environment file not found: %ENV_FILE%
    )
)

REM Create logs directory if it doesn't exist
IF NOT EXIST "%PROJECT_ROOT%\logs" (
    ECHO Creating logs directory
    MKDIR "%PROJECT_ROOT%\logs"
)

REM Set environment variables for Python
SET "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"
SET "DB_SERVER=%SERVER%"
SET "DB_USERNAME=%USERNAME%"
SET "DB_PASSWORD=%PASSWORD%"
SET "DB_DATABASE=%DATABASE%"
SET "HEALTH_INSURANCE_LOG_DIR=%PROJECT_ROOT%\logs"

REM Build command arguments
SET "CMD_ARGS="
IF NOT "%SERVER%"=="" (
    SET "CMD_ARGS=%CMD_ARGS% --server %SERVER%"
)
IF NOT "%USERNAME%"=="" (
    SET "CMD_ARGS=%CMD_ARGS% --username %USERNAME%"
)
IF NOT "%PASSWORD%"=="" (
    SET "CMD_ARGS=%CMD_ARGS% --password %PASSWORD%"
)
IF NOT "%DATABASE%"=="" (
    SET "CMD_ARGS=%CMD_ARGS% --database %DATABASE%"
)
IF EXIST "%ENV_FILE%" (
    SET "CMD_ARGS=%CMD_ARGS% --env-file "%ENV_FILE%""
)

REM Display the configuration being used
ECHO Using database configuration:
ECHO   Server: %SERVER%
ECHO   Database: %DATABASE%
ECHO   Username: %USERNAME%
ECHO   Environment File: %ENV_FILE%
ECHO   Project Root: %PROJECT_ROOT%

REM First run the Windows path fix script
python "%PROJECT_ROOT%\scripts\db\windows_path_fix.py"

REM Then run the initialization script with absolute path
python "%PROJECT_ROOT%\scripts\db\add_initial_data.py" %CMD_ARGS% --members "%MEMBERS%" --plans "%PLANS%" --providers "%PROVIDERS%" --log-file "%PROJECT_ROOT%\logs\add_initial_data.log"