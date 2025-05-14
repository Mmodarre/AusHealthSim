#!/bin/bash

# Add initial data to the Health Insurance AU database

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$DIR/.." && pwd )"

# Default values
SERVER=""
USERNAME=""
PASSWORD=""
DATABASE=""
MEMBERS=50
PLANS=15
PROVIDERS=30
ENV_FILE="$PROJECT_ROOT/config/db_config.env"

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
        --members)
            MEMBERS="$2"
            shift
            shift
            ;;
        --plans)
            PLANS="$2"
            shift
            shift
            ;;
        --providers)
            PROVIDERS="$2"
            shift
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --server      SQL Server hostname or IP"
            echo "  --username    SQL Server username"
            echo "  --password    SQL Server password"
            echo "  --database    Database name"
            echo "  --env-file    Path to environment file (default: $ENV_FILE)"
            echo "  --members     Number of members to add (default: $MEMBERS)"
            echo "  --plans       Number of plans to add (default: $PLANS)"
            echo "  --providers   Number of providers to add (default: $PROVIDERS)"
            echo "  -h, --help    Show this help message and exit"
            exit 0
            ;;
        *)
            echo "Unknown option: $key"
            echo "Use --help to see available options."
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

# Run the initialization script
python3 "$PROJECT_ROOT/scripts/db/add_initial_data.py" $CMD_ARGS --members "$MEMBERS" --plans "$PLANS" --providers "$PROVIDERS"