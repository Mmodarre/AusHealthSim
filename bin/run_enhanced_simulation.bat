@echo off
REM Wrapper script for the Enhanced Realistic Health Insurance Simulation

REM Get the directory of this script
set "DIR=%~dp0"
set "PROJECT_ROOT=%DIR%.."

REM Default environment file
set "ENV_FILE=%PROJECT_ROOT%\config\db_config.env"

REM Default values
set "START_DATE="
set "END_DATE="
set "MEMBERS_PER_DAY=10"
set "LOG_LEVEL=INFO"
set "RESET_MEMBERS="
set "USE_STATIC_DATA="
set "DISABLE_ENHANCED="

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse_args
if "%~1"=="--start-date" (
    set "START_DATE=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--end-date" (
    set "END_DATE=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--members-per-day" (
    set "MEMBERS_PER_DAY=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--log-level" (
    set "LOG_LEVEL=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--env-file" (
    set "ENV_FILE=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--reset-members" (
    set "RESET_MEMBERS=--reset-members"
    shift
    goto :parse_args
)
if "%~1"=="--use-static-data" (
    set "USE_STATIC_DATA=--use-static-data"
    shift
    goto :parse_args
)
if "%~1"=="--disable-enhanced" (
    set "DISABLE_ENHANCED=--disable-enhanced"
    shift
    goto :parse_args
)
echo Unknown option: %~1
echo Usage: %0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--members-per-day N] [--log-level LEVEL] [--env-file FILE] [--reset-members] [--use-static-data] [--disable-enhanced]
exit /b 1
:end_parse_args

REM Validate required arguments
if "%START_DATE%"=="" (
    echo Error: start-date is required
    echo Usage: %0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--members-per-day N] [--log-level LEVEL] [--env-file FILE] [--reset-members] [--use-static-data] [--disable-enhanced]
    exit /b 1
)
if "%END_DATE%"=="" (
    echo Error: end-date is required
    echo Usage: %0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--members-per-day N] [--log-level LEVEL] [--env-file FILE] [--reset-members] [--use-static-data] [--disable-enhanced]
    exit /b 1
)

REM Check if the environment file exists
if not exist "%ENV_FILE%" (
    echo Warning: Environment file %ENV_FILE% does not exist
    echo Using default database connection settings
)

REM Export environment variables from the environment file if it exists
if exist "%ENV_FILE%" (
    for /f "tokens=*" %%a in (%ENV_FILE%) do (
        set "%%a"
    )
)

REM Check if the database schema extensions have been applied
echo Checking if database schema extensions have been applied...
python -c "import sys; sys.path.insert(0, '%PROJECT_ROOT%'); from health_insurance_au.utils.db_utils import execute_query; try: result = execute_query(\"SELECT COUNT(*) AS TableCount FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'FraudIndicators' AND TABLE_SCHEMA = 'Insurance'\"); if result and result[0]['TableCount'] > 0: print('Schema extensions already applied'); sys.exit(0); else: print('Schema extensions not found'); sys.exit(1); except Exception as e: print(f'Error checking schema extensions: {e}'); sys.exit(1);"

REM If the schema extensions haven't been applied, ask to apply them
if %ERRORLEVEL% NEQ 0 (
    echo The database schema extensions for enhanced simulation are not applied.
    set /p apply_schema="Would you like to apply them now? (y/n): "
    if /i "%apply_schema%"=="y" (
        echo Applying database schema extensions...
        python "%PROJECT_ROOT%\scripts\apply_schema_extensions.py"
        if %ERRORLEVEL% NEQ 0 (
            echo Error applying schema extensions. Aborting.
            exit /b 1
        )
        echo Schema extensions applied successfully.
    ) else (
        echo Schema extensions are required for enhanced simulation. Aborting.
        exit /b 1
    )
)

REM Run the Python script
echo Running enhanced realistic simulation from %START_DATE% to %END_DATE% with %MEMBERS_PER_DAY% members per day...
python "%PROJECT_ROOT%\scripts\simulation\enhanced_realistic_simulation.py" ^
    --start-date "%START_DATE%" ^
    --end-date "%END_DATE%" ^
    --members-per-day "%MEMBERS_PER_DAY%" ^
    --log-level "%LOG_LEVEL%" ^
    %RESET_MEMBERS% ^
    %USE_STATIC_DATA% ^
    %DISABLE_ENHANCED%

echo Simulation completed!