# Dynamic Patient Data Generation

This document describes the implementation of dynamic patient data generation for the Health Insurance AU simulation.

## Overview

Previously, the simulation relied on a static JSON file (`health_insurance_demo_10k.json`) to generate patient data. The new implementation integrates with `generate_data.py` to dynamically generate realistic patient data on-the-fly.

## Implementation Details

### Directory Structure

```
health_insurance_au/
├── utils/
│   ├── data_generation/
│   │   ├── __init__.py
│   │   └── generate_data.py      # Moved from project root
│   └── dynamic_data_generator.py # New module
```

### New Files

1. **generate_data.py**: Moved to `health_insurance_au/utils/data_generation/` for better organization
   - Generates synthetic patient data with realistic demographics
   - Creates fixed records format compatible with the simulation

2. **dynamic_data_generator.py**: A new module in `health_insurance_au/utils/` that:
   - Integrates with `generate_data.py` to generate synthetic patient data
   - Converts the generated data to the format expected by the simulation
   - Provides a drop-in replacement for the existing data loading mechanism

### Modified Files

1. **simulation.py**: Updated to support dynamic data generation:
   - Added `use_dynamic_data` parameter to `add_members()` method
   - Added `use_dynamic_data` parameter to `run_daily_simulation()` method
   - Added `use_dynamic_data` parameter to `run_historical_simulation()` method

2. **realistic_simulation.py**: Updated to support dynamic data generation:
   - Added `use_dynamic_data` parameter to `run_realistic_simulation()` function
   - Added `--use-static-data` command-line option to the main function

3. **run_realistic_simulation.sh**: Updated to support the new `--use-static-data` option

## Usage

### Command Line

The simulation now defaults to using dynamically generated data. To use the static JSON file instead, use the `--use-static-data` option:

```bash
./bin/run_realistic_simulation.sh \
  --start-date 2023-01-01 \
  --end-date 2023-01-31 \
  --members-per-day 10 \
  --use-static-data
```

### Python API

When using the simulation API, you can specify whether to use dynamic data:

```python
from health_insurance_au.simulation.simulation import HealthInsuranceSimulation

# Create a simulation instance
simulation = HealthInsuranceSimulation()

# Run with dynamic data (default)
simulation.run_daily_simulation(
    simulation_date=date.today(),
    add_new_members=True,
    new_members_count=10,
    use_dynamic_data=True  # This is the default
)

# Run with static data
simulation.run_daily_simulation(
    simulation_date=date.today(),
    add_new_members=True,
    new_members_count=10,
    use_dynamic_data=False
)
```

## Testing

To test the dynamic data generation functionality, run:

```bash
python3 tests/test_dynamic_data.py
```

This will:
1. Generate a sample of dynamic patient data
2. Convert it to Member objects
3. Run a simple simulation using the dynamic data

## Benefits

- **Unlimited Data**: No longer limited by the size of the static JSON file
- **Realistic Variation**: Each run generates different, realistic patient data
- **Customizable**: The `generate_data.py` script can be modified to adjust demographics, etc.
- **Reduced Disk Usage**: No need to store large JSON files with sample data