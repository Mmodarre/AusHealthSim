# Adjustable Logging System

This document describes the adjustable logging system implemented in the Health Insurance AU simulation project.

## Overview

The logging system allows you to control the verbosity of log output during development and production. You can:

1. Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
2. Redirect logs to a file (in addition to console output)
3. Configure logging via command-line arguments or environment variables

## Log Levels

The following log levels are available, in order of increasing severity:

- **DEBUG**: Detailed information, typically useful only for diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARNING**: An indication that something unexpected happened, or may happen in the future
- **ERROR**: Due to a more serious problem, the software has not been able to perform a function
- **CRITICAL**: A serious error, indicating that the program itself may be unable to continue running

## Usage

### Command-line Arguments

All scripts support the following command-line arguments for logging:

```bash
--log-level LEVEL  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
--log-file FILE    # Log to this file (in addition to console)
```

Example:

```bash
python monitor_cdc.py --log-level DEBUG --log-file logs/cdc_debug.log
```

### Environment Variable

You can set the `HEALTH_INSURANCE_LOG_LEVEL` environment variable to control the default log level:

```bash
export HEALTH_INSURANCE_LOG_LEVEL=DEBUG
python monitor_cdc.py  # Will use DEBUG level
```

### Helper Script

Use the `set_log_level.sh` script to easily set the logging level:

```bash
# Set log level to DEBUG for this run
./set_log_level.sh --level DEBUG

# Log to specific file with INFO level
./set_log_level.sh --level INFO --file logs/app.log

# Set WARNING level as environment variable (persists for current session)
./set_log_level.sh --level WARNING --env
```

## Default Configuration

The default logging configuration is stored in `health_insurance_au/config.py`:

```python
LOG_CONFIG = {
    'default_level': 'INFO',  # Default log level if not specified
    'log_dir': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs'),
    'log_file': 'health_insurance_au.log',  # Default log file name
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
```

## Implementation Details

The logging system is implemented in `health_insurance_au/utils/logging_config.py` and provides:

- Centralized logging configuration
- Support for multiple handlers (console and file)
- Consistent log formatting
- Dynamic log level adjustment

## Best Practices

1. Use the appropriate log level for each message:
   - DEBUG for detailed diagnostic information
   - INFO for general operational information
   - WARNING for potential issues
   - ERROR for actual errors
   - CRITICAL for fatal errors

2. Include context in log messages:
   - What happened
   - Where it happened
   - Why it happened (if known)

3. Use structured logging for complex data:
   ```python
   logger.debug("Processing data: %s", json.dumps(data, indent=2))
   ```

4. Set lower log levels during development and higher levels in production.