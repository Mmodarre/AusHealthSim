#!/bin/bash

# Run a complete simulation

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Default environment file
ENV_FILE="$DIR/health_insurance_au/db_config.env"

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

# Step 1: Initialize the database
echo "Step 1: Initializing the database..."
"$DIR/initialize_db.sh" --env-file "$ENV_FILE" --drop

# Step 2: Add initial data
echo "Step 2: Adding initial data..."
"$DIR/add_initial_data.sh" --env-file "$ENV_FILE" --members 50 --plans 15 --providers 30

# Step 3: Run a historical simulation
echo "Step 3: Running historical simulation..."
python3 -m health_insurance_au.main historical --start-date 2023-01-01 --end-date 2023-01-31 --frequency weekly

echo "Simulation completed!"