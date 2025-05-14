#!/bin/bash

# Wrapper script for the Realistic Health Insurance Simulation

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Default environment file
ENV_FILE="$DIR/health_insurance_au/db_config.env"

# Default values
START_DATE=""
END_DATE=""
MEMBERS_PER_DAY=10
LOG_LEVEL="INFO"
RESET_MEMBERS=""

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
        *)
            echo "Unknown option: $key"
            echo "Usage: $0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--members-per-day N] [--log-level LEVEL] [--env-file FILE] [--reset-members]"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$START_DATE" ] || [ -z "$END_DATE" ]; then
    echo "Error: start-date and end-date are required"
    echo "Usage: $0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--members-per-day N] [--log-level LEVEL] [--env-file FILE]"
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

# Run the Python script
echo "Running realistic simulation from $START_DATE to $END_DATE with $MEMBERS_PER_DAY members per day..."
python3 "$DIR/realistic_simulation.py" \
    --start-date "$START_DATE" \
    --end-date "$END_DATE" \
    --members-per-day "$MEMBERS_PER_DAY" \
    --log-level "$LOG_LEVEL" \
    $RESET_MEMBERS

echo "Simulation completed!"