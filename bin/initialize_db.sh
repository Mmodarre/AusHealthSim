#!/bin/bash

# Initialize the Health Insurance AU database

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Default values
SERVER=""
USERNAME=""
PASSWORD=""
DATABASE=""
DROP=false
ENV_FILE="$DIR/health_insurance_au/db_config.env"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --server)
            SERVER="$2"
            shift
            shift
            ;;
        --username)
            USERNAME="$2"
            shift
            shift
            ;;
        --password)
            PASSWORD="$2"
            shift
            shift
            ;;
        --database)
            DATABASE="$2"
            shift
            shift
            ;;
        --env-file)
            ENV_FILE="$2"
            shift
            shift
            ;;
        --drop)
            DROP=true
            shift
            ;;
        *)
            echo "Unknown option: $key"
            exit 1
            ;;
    esac
done

# Build command arguments
CMD_ARGS=""
if [ -n "$SERVER" ]; then
    CMD_ARGS="$CMD_ARGS --server $SERVER"
fi
if [ -n "$USERNAME" ]; then
    CMD_ARGS="$CMD_ARGS --username $USERNAME"
fi
if [ -n "$PASSWORD" ]; then
    CMD_ARGS="$CMD_ARGS --password $PASSWORD"
fi
if [ -n "$DATABASE" ]; then
    CMD_ARGS="$CMD_ARGS --database $DATABASE"
fi
if [ -n "$ENV_FILE" ]; then
    CMD_ARGS="$CMD_ARGS --env-file $ENV_FILE"
fi
if [ "$DROP" = true ]; then
    CMD_ARGS="$CMD_ARGS --drop"
fi

# Run the initialization script
python3 "$DIR/initialize_db.py" $CMD_ARGS