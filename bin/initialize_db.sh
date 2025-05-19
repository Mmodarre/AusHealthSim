#!/bin/bash

# Initialize the Health Insurance AU database

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$DIR/.." && pwd )"

# Default values
SERVER=""
USERNAME=""
PASSWORD=""
DATABASE=""
DROP=false
ENV_FILE="$PROJECT_ROOT/config/db_config.env"
INCLUDE_ENHANCED=true

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
        --include-enhanced)
            INCLUDE_ENHANCED=true
            shift
            ;;
        *)
            echo "Unknown option: $key"
            echo "Usage: $0 [--server SERVER] [--username USERNAME] [--password PASSWORD] [--database DATABASE] [--env-file FILE] [--drop] [--include-enhanced]"
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
echo "Initializing database..."
python3 "$PROJECT_ROOT/scripts/db/initialize_db.py" $CMD_ARGS

# If enhanced mode is enabled, apply the schema extensions
if [ "$INCLUDE_ENHANCED" = true ]; then
    echo "Applying enhanced database schema..."
    python3 "$PROJECT_ROOT/scripts/db/execute_sql.py" "$PROJECT_ROOT/scripts/extend_database_schema.sql" $CMD_ARGS
    
    echo "Adding enhanced initial data..."
    python3 "$PROJECT_ROOT/scripts/db/add_enhanced_data.py" $CMD_ARGS
fi

echo "Database initialization completed!"