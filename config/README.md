# Configuration Directory

This directory contains configuration files for the Health Insurance Simulation project.

## Available Configuration Files

- `db_config.env` - Database connection configuration
- `db_config.env.example` - Example database configuration template
- `logging.conf` - Logging configuration
- `simulation.conf` - Simulation parameters configuration

## Usage

### Database Configuration

Copy the example configuration file and edit it with your database credentials:

```bash
cp config/db_config.env.example config/db_config.env
# Edit config/db_config.env with your database credentials
```

The database configuration file should contain the following variables:

```
DB_SERVER=your_server
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

### Logging Configuration

The logging configuration file uses the Python logging configuration format. You can adjust the logging levels, handlers, and formatters as needed.

### Simulation Configuration

The simulation configuration file contains parameters for running simulations, including:

- Start and end dates
- Simulation frequency
- Member growth and churn rates
- Policy type distributions
- Claim frequencies and amounts
- Provider distributions

Edit this file to customize your simulation parameters.