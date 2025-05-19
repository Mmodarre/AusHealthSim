#!/bin/bash

# Wrapper script for the Enhanced Realistic Health Insurance Simulation

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$DIR/.." && pwd )"

# Default environment file
ENV_FILE="$PROJECT_ROOT/config/db_config.env"

# Default values
START_DATE=""
END_DATE=""
MEMBERS_PER_DAY=10
LOG_LEVEL="INFO"
RESET_MEMBERS=""
USE_STATIC_DATA=""
DISABLE_ENHANCED=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --start-date)
            START_DATE="$2"
            shift
            shift
            ;;
        --end-date)
            END_DATE="$2"
            shift
            shift
            ;;
        --members-per-day)
            MEMBERS_PER_DAY="$2"
            shift
            shift
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift
            shift
            ;;
        --env-file)
            ENV_FILE="$2"
            shift
            shift
            ;;
        --reset-members)
            RESET_MEMBERS="--reset-members"
            shift
            ;;
        --use-static-data)
            USE_STATIC_DATA="--use-static-data"
            shift
            ;;
        --disable-enhanced)
            DISABLE_ENHANCED="--disable-enhanced"
            shift
            ;;
        *)
            echo "Unknown option: $key"
            echo "Usage: $0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--members-per-day N] [--log-level LEVEL] [--env-file FILE] [--reset-members] [--use-static-data] [--disable-enhanced]"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$START_DATE" ] || [ -z "$END_DATE" ]; then
    echo "Error: start-date and end-date are required"
    echo "Usage: $0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--members-per-day N] [--log-level LEVEL] [--env-file FILE] [--reset-members] [--use-static-data] [--disable-enhanced]"
    exit 1
fi

# Check if the environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Warning: Environment file $ENV_FILE does not exist"
    echo "Using default database connection settings"
fi

# Export environment variables from the environment file if it exists
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Check if the database schema extensions have been applied
echo "Checking if database schema extensions have been applied..."
python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from health_insurance_au.utils.db_utils import execute_query
try:
    result = execute_query(\"SELECT COUNT(*) AS TableCount FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'FraudIndicators' AND TABLE_SCHEMA = 'Insurance'\")
    if result and result[0]['TableCount'] > 0:
        print('Schema extensions already applied')
        sys.exit(0)
    else:
        print('Schema extensions not found')
        sys.exit(1)
except Exception as e:
    print(f'Error checking schema extensions: {e}')
    sys.exit(1)
"

# If the schema extensions haven't been applied, ask to apply them
if [ $? -ne 0 ]; then
    echo "The database schema extensions for enhanced simulation are not applied."
    read -p "Would you like to apply them now? (y/n): " apply_schema
    if [[ $apply_schema == "y" || $apply_schema == "Y" ]]; then
        echo "Applying database schema extensions..."
        python3 "$PROJECT_ROOT/scripts/apply_schema_extensions.py"
        if [ $? -ne 0 ]; then
            echo "Error applying schema extensions. Aborting."
            exit 1
        fi
        echo "Schema extensions applied successfully."
    else
        echo "Schema extensions are required for enhanced simulation. Aborting."
        exit 1
    fi
fi

# Run the Python script
echo "Running enhanced realistic simulation from $START_DATE to $END_DATE with $MEMBERS_PER_DAY members per day..."
python3 "$PROJECT_ROOT/scripts/simulation/enhanced_realistic_simulation.py" \
    --start-date "$START_DATE" \
    --end-date "$END_DATE" \
    --members-per-day "$MEMBERS_PER_DAY" \
    --log-level "$LOG_LEVEL" \
    $RESET_MEMBERS \
    $USE_STATIC_DATA \
    $DISABLE_ENHANCED

echo "Simulation completed!"