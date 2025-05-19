@echo off
REM Initialize the Health Insurance AU database

REM Get the directory of this script
SET "SCRIPT_DIR=%~dp0"
SET "PROJECT_ROOT=%SCRIPT_DIR%.."

REM Default values
SET "SERVER="
SET "USERNAME="
SET "PASSWORD="
SET "DATABASE="
SET "DROP="
SET "ENV_FILE=%PROJECT_ROOT%\config\db_config.env"
SET "INCLUDE_ENHANCED=true"

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
IF "%~1"=="--drop" (
    SET "DROP=--drop"
    GOTO next_arg
)
IF "%~1"=="--include-enhanced" (
    SET "INCLUDE_ENHANCED=true"
    GOTO next_arg
)
ECHO Unknown option: %~1
ECHO Usage: %0 [--server SERVER] [--username USERNAME] [--password PASSWORD] [--database DATABASE] [--env-file FILE] [--drop] [--include-enhanced]
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

REM Create logs directory if it doesn't exist
IF NOT EXIST "%PROJECT_ROOT%\logs" (
    ECHO Creating logs directory
    MKDIR "%PROJECT_ROOT%\logs"
)

REM Set environment variables for Python
SET "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"
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

REM Run the initialization script
ECHO Initializing database...
python "%PROJECT_ROOT%\scripts\db\initialize_db.py" %CMD_ARGS% %DROP%

REM If enhanced mode is enabled, apply the schema extensions
IF "%INCLUDE_ENHANCED%"=="true" (
    ECHO Applying enhanced database schema...
    python "%PROJECT_ROOT%\scripts\db\execute_sql.py" "%PROJECT_ROOT%\scripts\extend_database_schema.sql" %CMD_ARGS%
    
    ECHO Adding enhanced initial data...
    python "%PROJECT_ROOT%\scripts\db\add_enhanced_data.py" %CMD_ARGS%
)

ECHO Database initialization completed!