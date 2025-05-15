# Data Generation Utilities

This directory contains utilities for generating synthetic patient data for the Health Insurance AU simulation.

## Files

- `generate_data.py`: Core module for generating realistic synthetic patient data
  - Uses the Faker library to create demographically realistic profiles
  - Supports generating life stages and variants for each patient
  - Creates fixed records format compatible with the simulation

## Usage

The main function exposed by this package is `generate_fixed_records`:

```python
from health_insurance_au.utils.data_generation import generate_fixed_records

# Generate 10 patient records
patient_records = generate_fixed_records(10)
```

For more advanced usage, see `dynamic_data_generator.py` in the parent directory, which provides integration with the simulation system.

## Command Line Usage

The `generate_data.py` script can also be run directly:

```bash
python -m health_insurance_au.utils.data_generation.generate_data --num_patients 100 --output patients.json
```

## Parameters

- `num_patients`: Number of patients to generate (default: 10)
- `output`: Output JSON file (default: fixed_records.json)
- `seed`: Random seed for reproducibility (optional)