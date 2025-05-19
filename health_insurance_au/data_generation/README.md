# Enhanced Data Generation

This module provides enhanced data generation capabilities for the Health Insurance AU simulation, focusing on:

1. Fraud Detection
2. Claims Management
3. Cost & Financial Analysis

## Key Components

### Core Generators

- **FraudPatternGenerator**: Creates realistic fraud-like patterns in claims data
- **FinancialTransactionGenerator**: Generates premium, claim payment, and administrative transactions
- **ProviderBillingGenerator**: Creates varied billing patterns across different provider types
- **ClaimPatternGenerator**: Generates claims with realistic distributions and patterns
- **ActuarialDataGenerator**: Creates actuarial metrics and cost data

### Controllers

- **SimulationOrchestrator**: Coordinates all data generation activities

## Database Schema Extensions

The enhanced simulation adds the following extensions to the database schema:

### Extended Tables

- **Insurance.Members**: Added risk profile attributes
  - RiskScore
  - ChronicConditionFlag
  - LifestyleRiskFactor
  - ClaimFrequencyTier
  - PredictedChurn

- **Insurance.Policies**: Added APRA entity codes and risk-adjusted loading
  - APRAEntityCode
  - RiskAdjustedLoading
  - UnderwritingScore
  - PolicyValueSegment
  - RetentionRiskScore

- **Insurance.Claims**: Added potential fraud pattern fields
  - AnomalyScore
  - FraudIndicatorCount
  - UnusualPatternFlag
  - ClaimComplexityScore
  - ClaimAdjustmentHistory
  - ReviewFlag

- **Insurance.Providers**: Added billing pattern attributes
  - BillingPatternScore
  - AvgClaimValue
  - ClaimFrequencyRating
  - SpecialtyRiskFactor
  - ComplianceScore

### New Tables

- **Insurance.FraudIndicators**: Reference data for fraud detection
- **Insurance.FinancialTransactions**: Financial transaction records
- **Insurance.ActuarialMetrics**: Reference data for actuarial analysis
- **Insurance.ClaimPatterns**: Tracking of claim patterns

## Usage

### Command Line Interface

The enhanced simulation can be run using the main CLI:

```bash
# Run enhanced simulation for current date
python -m health_insurance_au.main enhanced

# Run enhanced simulation for a specific date
python -m health_insurance_au.main enhanced --date 2023-05-01

# Run specific features only
python -m health_insurance_au.main enhanced --fraud-patterns --claim-patterns

# Run historical simulation with enhanced features
python -m health_insurance_au.main historical --start-date 2023-01-01 --end-date 2023-03-31 --frequency monthly --enhanced
```

### Python API

You can also use the Python API directly:

```python
from datetime import date
from health_insurance_au.data_generation.enhanced_simulation import run_enhanced_simulation

# Configure the simulation
config = {
    'generate_member_risk_profiles': True,
    'generate_policy_risk_attributes': True,
    'generate_provider_billing_attributes': True,
    'apply_fraud_patterns': True,
    'generate_claim_patterns': True,
    'generate_financial_transactions': True,
    'generate_actuarial_metrics': True,
    'actuarial_metrics_count': 50,
    'claim_pattern_count': 20,
    'financial_transaction_count': 30
}

# Run the simulation
results = run_enhanced_simulation(date.today(), config)
```

## Database Setup

Before running the enhanced simulation, you need to apply the database schema extensions:

```bash
python scripts/apply_schema_extensions.py
```

This will add the necessary columns and tables to the database.