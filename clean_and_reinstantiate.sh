#!/bin/bash

# Script to clean up project and reinstantiate the application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=== Cleaning up project ==="

# Clean up Python compiled files
echo "Cleaning Python compiled files..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
echo "Done."

# Clean up any CDC reports
echo "Cleaning up reports..."
if [ -d "reports" ]; then
    rm -rf reports
    mkdir reports
else
    mkdir -p reports
fi
echo "Done."

# Default environment file
ENV_FILE="$SCRIPT_DIR/health_insurance_au/db_config.env"

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

echo "=== Dropping and recreating database ==="
echo "Using environment file: $ENV_FILE"

# Drop and recreate the database
echo "Running initialize_db.sh with --drop option..."
"$SCRIPT_DIR/initialize_db.sh" --env-file "$ENV_FILE" --drop
if [ $? -ne 0 ]; then
    echo "Failed to initialize database. Exiting."
    exit 1
fi
echo "Database initialized successfully."

# Enable CDC
echo "=== Enabling CDC ==="
echo "Running enable_cdc.sh..."
"$SCRIPT_DIR/enable_cdc.sh" --env-file "$ENV_FILE"
if [ $? -ne 0 ]; then
    echo "Failed to enable CDC. Exiting."
    exit 1
fi
echo "CDC enabled successfully."

# Add initial data
# echo "=== Adding initial data ==="
# echo "Running add_initial_data.sh..."
# "$SCRIPT_DIR/add_initial_data.sh" --env-file "$ENV_FILE" --members 5000 --plans 50 --providers 2000
# if [ $? -ne 0 ]; then
#     echo "Failed to add initial data. Exiting."
#     exit 1
# fi
# echo "Initial data added successfully."

echo "=== Database reinstantiated successfully ==="
# echo "You can now run simulations using run_simulation.sh or run_complete_simulation.sh"