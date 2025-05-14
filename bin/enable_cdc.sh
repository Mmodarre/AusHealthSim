#!/bin/bash

# Script to enable CDC on the Health Insurance AU database

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Default values
ENV_FILE="$PROJECT_ROOT/config/db_config.env"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --env-file)
            ENV_FILE="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $key"
            exit 1
            ;;
    esac
done

# Run the Python script to enable CDC
echo "Enabling CDC using environment file: $ENV_FILE..."
python3 "$PROJECT_ROOT/scripts/db/enable_cdc.py" --env-file "$ENV_FILE"

echo "CDC setup completed."