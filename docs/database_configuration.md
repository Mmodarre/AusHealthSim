# Database Configuration Guide

This document provides detailed information about configuring database connections for the Australian Health Insurance Simulation project.

## Configuration Methods

The project supports multiple methods for configuring database connections, with the following order of precedence:

1. Command-line arguments (highest precedence)
2. Environment variables
3. Configuration file (db_config.env)
4. Default values (lowest precedence)

## Environment Variables

You can set the following environment variables to configure the database connection:

```bash
export DB_SERVER=your_server_address
export DB_DATABASE=your_database_name
export DB_USERNAME=your_username
export DB_PASSWORD=your_password
export DB_DRIVER="{ODBC Driver 17 for SQL Server}"
```

These environment variables will be used by all scripts in the project.

## Configuration File

The project can read database configuration from a file named `db_config.env` in the `health_insurance_au` directory. This file should contain the following variables:

```
DB_SERVER=your_server_address
DB_DATABASE=your_database_name
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_DRIVER={ODBC Driver 17 for SQL Server}
```

A template file `db_config.env.example` is provided in the repository. Copy this file to `db_config.env` and update it with your actual database credentials:

```bash
cp health_insurance_au/db_config.env.example health_insurance_au/db_config.env
# Edit the file with your preferred text editor
nano health_insurance_au/db_config.env
```

## Command-line Arguments

All Python scripts in the project accept command-line arguments to override the database configuration:

```bash
python initialize_db.py --server your_server_address --username your_username --password your_password --database your_database_name
```

You can also specify a custom environment file:

```bash
python initialize_db.py --env-file /path/to/your/env/file
```

## Implementation Details

The database configuration is loaded through the `get_db_config()` function in `health_insurance_au/utils/env_utils.py`. This function:

1. Sets default values
2. Loads values from environment variables if available
3. Overrides with values from the specified environment file if provided
4. Returns a dictionary with the configuration

The `DB_CONFIG` dictionary in `health_insurance_au/config.py` is initialized using this function.

## Security Considerations

### Local Development

For local development:

- Use the `db_config.env` file for convenience
- Ensure this file is listed in `.gitignore` to prevent accidentally committing credentials
- Never commit actual credentials to version control

### Production Environments

For production environments:

- Consider using environment variables set in the deployment environment
- Use a secure vault or key management service for storing credentials
- Implement credential rotation policies

### Connection String Security

The connection string is constructed in the `get_connection()` function in `health_insurance_au/utils/db_utils.py`. This function:

- Creates a connection string using the configuration values
- Opens a connection to the database
- Uses a context manager to ensure proper connection cleanup

## Troubleshooting

### Connection Issues

If you encounter database connection issues:

1. Verify your credentials are correct
2. Check that the SQL Server instance is running and accessible from your network
3. Ensure the ODBC Driver 17 for SQL Server is installed
4. Check for firewall rules that might block the connection
5. Enable debug logging to see detailed connection information:
   ```bash
   python your_script.py --log-level DEBUG
   ```

### Configuration Precedence

If your configuration isn't being applied as expected, remember the order of precedence:

1. Command-line arguments override everything
2. Environment variables override the configuration file
3. Configuration file overrides default values

Use the `--log-level DEBUG` option to see which configuration values are being used.