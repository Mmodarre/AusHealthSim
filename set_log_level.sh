#!/bin/bash
# set_log_level.sh - Set logging level for the Health Insurance AU simulation

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Set logging level for the Health Insurance AU simulation"
    echo ""
    echo "Options:"
    echo "  -l, --level LEVEL   Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    echo "  -f, --file FILE     Set log file path"
    echo "  -e, --env           Set level as environment variable (persists for current session)"
    echo "  -h, --help          Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --level DEBUG                # Set log level to DEBUG for this run"
    echo "  $0 --level INFO --file logs/app.log  # Log to specific file with INFO level"
    echo "  $0 --level WARNING --env        # Set WARNING level as environment variable"
    exit 1
}

# Default values
LOG_LEVEL=""
LOG_FILE=""
SET_ENV=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -l|--level)
            LOG_LEVEL="$2"
            shift
            shift
            ;;
        -f|--file)
            LOG_FILE="$2"
            shift
            shift
            ;;
        -e|--env)
            SET_ENV=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate log level
if [[ -n "$LOG_LEVEL" ]]; then
    if [[ ! "$LOG_LEVEL" =~ ^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$ ]]; then
        echo "Error: Invalid log level. Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
        exit 1
    fi
else
    echo "Error: Log level must be specified"
    usage
fi

# Set environment variable if requested
if [[ "$SET_ENV" = true ]]; then
    export HEALTH_INSURANCE_LOG_LEVEL="$LOG_LEVEL"
    echo "Environment variable HEALTH_INSURANCE_LOG_LEVEL set to $LOG_LEVEL"
    echo "This will affect all scripts run in the current terminal session"
    echo "To make this permanent, add the following to your ~/.bashrc or ~/.zshrc:"
    echo "export HEALTH_INSURANCE_LOG_LEVEL=$LOG_LEVEL"
fi

# Display configuration
echo "Log level set to: $LOG_LEVEL"
if [[ -n "$LOG_FILE" ]]; then
    echo "Log file: $LOG_FILE"
fi

# Provide examples of how to use this configuration
echo ""
echo "Examples of how to use this configuration:"
if [[ "$SET_ENV" = true ]]; then
    echo "Environment variable is set, so you can simply run:"
    echo "python monitor_cdc.py"
    echo "python add_initial_data.py"
else
    echo "python monitor_cdc.py --log-level $LOG_LEVEL"
    if [[ -n "$LOG_FILE" ]]; then
        echo "python monitor_cdc.py --log-level $LOG_LEVEL --log-file \"$LOG_FILE\""
    fi
    
    echo "python add_initial_data.py --log-level $LOG_LEVEL"
    if [[ -n "$LOG_FILE" ]]; then
        echo "python add_initial_data.py --log-level $LOG_LEVEL --log-file \"$LOG_FILE\""
    fi
fi