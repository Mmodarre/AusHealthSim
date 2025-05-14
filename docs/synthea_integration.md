# Synthea Integration Guide

This document provides detailed information about the integration with Synthea synthetic patient data in the Australian Health Insurance Simulation project.

## Overview

[Synthea](https://synthetichealth.github.io/synthea/) is an open-source synthetic patient generator that creates realistic but synthetic patient records. This project integrates Synthea data to enhance the health insurance simulation with detailed clinical information.

The integration allows:
- Importing Synthea FHIR patient data into the insurance database
- Linking synthetic patients to insurance members
- Generating insurance claims based on Synthea encounters
- Creating a more realistic end-to-end healthcare simulation

## Synthea Adaptation for Australian Context

The standard Synthea data is adapted for the Australian healthcare context with:

1. **Australian Demographics**:
   - Australian postcodes and states
   - Adjusted disease prevalence to match Australian population
   - Australian naming patterns

2. **Australian Healthcare System**:
   - Medicare Benefits Schedule (MBS) item numbers
   - Pharmaceutical Benefits Scheme (PBS) medications
   - Australian hospital and provider naming conventions

3. **Insurance-Specific Adaptations**:
   - Hospital tiers (Basic, Bronze, Silver, Gold)
   - Waiting periods
   - Lifetime Health Cover (LHC) loading
   - Private Health Insurance (PHI) rebate

## Database Structure

The integration uses three main tables in the `Integration` schema:

1. **Integration.SyntheaPatients**:
   - Links Synthea patients to insurance members
   - Stores the complete FHIR Patient resource as JSON
   - Tracks import date and modifications

2. **Integration.SyntheaEncounters**:
   - Links Synthea encounters to insurance claims
   - Stores the complete FHIR Encounter resource as JSON
   - Contains references to the patient and provider

3. **Integration.SyntheaProcedures**:
   - Links Synthea procedures to insurance claims
   - Stores the complete FHIR Procedure resource as JSON
   - Contains references to the encounter and patient

## Integration Process

### Generating Synthea Data

1. Download and set up Synthea from [GitHub](https://github.com/synthetichealth/synthea)
2. Configure Synthea for Australian context (see configuration examples in `synthea_configs/`)
3. Generate patient data:
   ```bash
   ./run_synthea -p 100 Australia
   ```
4. The generated FHIR JSON files will be in the `output/fhir` directory

### Importing Synthea Data

Use the `import_synthea.py` script to import Synthea data:

```bash
python import_synthea.py --dir path/to/synthea/output/fhir --patients 100
```

Options:
- `--dir`: Directory containing Synthea FHIR JSON files (required)
- `--patients`: Limit on number of patients to import (default: all)
- `--encounters`: Limit on number of encounters to import (default: all)
- `--procedures`: Limit on number of procedures to import (default: all)
- `--skip-patients`: Skip patient import
- `--skip-encounters`: Skip encounter import
- `--skip-procedures`: Skip procedure import

### Generating Claims from Synthea Data

Use the `generate_synthea_claims.py` script to generate insurance claims from Synthea encounters:

```bash
python generate_synthea_claims.py --claims 50
```

Options:
- `--claims`: Number of claims to generate (default: 50)
- `--start-date`: Start date for claims (default: 30 days ago)
- `--end-date`: End date for claims (default: today)
- `--hospital-ratio`: Ratio of hospital claims (default: 0.2)

## Integration Architecture

The integration follows these steps:

1. **Patient-Member Matching**:
   - Synthea patients are matched to insurance members
   - Matching uses name, date of birth, and address
   - New members are created if no match is found

2. **Encounter Processing**:
   - Encounters are processed to extract service information
   - Hospital encounters are mapped to hospital claims
   - Other encounters are mapped to general treatment claims

3. **MBS Code Mapping**:
   - Synthea SNOMED codes are mapped to Australian MBS codes
   - Default MBS codes are used when no mapping exists
   - MBS codes determine Medicare benefits and gap amounts

4. **Claim Generation**:
   - Claims are generated with appropriate service dates
   - Claim amounts are calculated based on service type
   - Excess and gap amounts are applied according to policy

## Customizing the Integration

### Mapping Configuration

Mapping files in the `mappings/` directory control how Synthea data is interpreted:

- `snomed_to_mbs.json`: Maps SNOMED codes to MBS item numbers
- `provider_types.json`: Maps Synthea organization types to provider types
- `encounter_types.json`: Maps Synthea encounter types to claim types

### Integration Parameters

The integration behavior can be customized in `health_insurance_au/config.py`:

- `SYNTHEA_INTEGRATION`: General integration settings
- `SYNTHEA_CLAIM_GENERATION`: Claim generation parameters
- `SYNTHEA_MBS_MAPPING`: MBS mapping parameters

## Advanced Usage

### Custom FHIR Resources

You can import custom FHIR resources by extending the `SyntheaImporter` class:

```python
from health_insurance_au.integration.synthea import SyntheaImporter

class CustomImporter(SyntheaImporter):
    def process_custom_resource(self, resource):
        # Custom processing logic
        pass
        
importer = CustomImporter()
importer.import_directory('path/to/fhir/files')
```

### Bidirectional Integration

The integration supports bidirectional data flow:

1. **Synthea to Insurance**: Import patient data and generate claims
2. **Insurance to Synthea**: Export member data to create targeted Synthea patients

Use the `export_members_for_synthea.py` script for the second direction:

```bash
python export_members_for_synthea.py --members 50 --output members.csv
```

## Troubleshooting

### Common Issues

- **Missing FHIR resources**: Ensure the Synthea output directory contains valid FHIR JSON files
- **Mapping errors**: Check the mapping files for missing codes
- **Database errors**: Verify database connection and permissions
- **Duplicate patients**: Use the `--skip-patients` option if patients are already imported

### Logging

Enable detailed logging for troubleshooting:

```bash
python import_synthea.py --dir path/to/fhir --log-level DEBUG
```

## Additional Resources

- [Synthea GitHub Repository](https://github.com/synthetichealth/synthea)
- [FHIR Standard Documentation](https://www.hl7.org/fhir/)
- [Medicare Benefits Schedule](https://www.mbsonline.gov.au/)