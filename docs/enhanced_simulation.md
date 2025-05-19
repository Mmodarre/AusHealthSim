# Enhanced Simulation Features

This document describes the enhanced simulation features that extend the base Australian Health Insurance Simulation system to support fraud detection, financial analysis, and actuarial metrics.

## Overview

The enhanced simulation adds capabilities for:

1. **Fraud Detection**: Identifying suspicious claims and billing patterns
2. **Financial Analysis**: Tracking detailed financial transactions
3. **Risk Profiling**: Assessing member and policy risk attributes
4. **Actuarial Metrics**: Generating metrics for financial performance analysis

## Database Schema Extensions

The enhanced simulation extends the standard database schema with additional tables and columns:

### Extended Tables

1. **Insurance.Members**
   - `RiskScore`: Overall risk score for the member
   - `ChronicConditionFlag`: Whether the member has chronic conditions
   - `LifestyleRiskFactor`: Risk factor based on lifestyle
   - `ClaimFrequencyTier`: Categorization of claim frequency
   - `PredictedChurn`: Probability of member churning

2. **Insurance.Policies**
   - `APRAEntityCode`: APRA entity code for regulatory reporting
   - `RiskAdjustedLoading`: Risk-based loading percentage
   - `UnderwritingScore`: Score from underwriting assessment
   - `PolicyValueSegment`: Value segment categorization
   - `RetentionRiskScore`: Risk score for retention

3. **Insurance.Claims**
   - `AnomalyScore`: Score indicating claim anomaly level
   - `FraudIndicatorCount`: Number of fraud indicators triggered
   - `UnusualPatternFlag`: Flag for unusual claim patterns
   - `ClaimComplexityScore`: Complexity score for the claim
   - `ClaimAdjustmentHistory`: History of adjustments made
   - `ReviewFlag`: Flag indicating claim needs review

4. **Insurance.Providers**
   - `BillingPatternScore`: Score for provider billing patterns
   - `AvgClaimValue`: Average claim value for the provider
   - `ClaimFrequencyRating`: Rating of claim frequency
   - `SpecialtyRiskFactor`: Risk factor for the specialty
   - `ComplianceScore`: Score for provider compliance

### New Tables

1. **Insurance.FraudIndicators**
   - Reference table for fraud indicators
   - Contains indicator codes, descriptions, and detection logic

2. **Insurance.FinancialTransactions**
   - Detailed tracking of all financial transactions
   - Links to related entities (claims, policies, etc.)

3. **Insurance.ActuarialMetrics**
   - Reference table for actuarial metrics
   - Contains metrics by demographic segments

4. **Insurance.ClaimPatterns**
   - Tracking of claim patterns for analysis
   - Links members and providers to detected patterns

## Data Generation Modules

The enhanced simulation includes additional Python modules for generating realistic data:

1. **fraud_patterns.py**
   - Generates realistic fraud-like patterns in claims
   - Supports different anomaly types (duplicate services, upcoding, etc.)

2. **financial_transactions.py**
   - Generates premium payment transactions
   - Generates claim payment transactions
   - Generates miscellaneous transactions (refunds, adjustments, fees)

3. **provider_billing.py**
   - Generates billing pattern attributes for providers
   - Analyzes provider claim patterns
   - Supports different provider types with unique billing profiles

4. **claim_patterns.py**
   - Generates enhanced claims with realistic patterns
   - Generates claim clusters to create patterns
   - Supports weighted distributions for claim types and services

5. **actuarial_data.py**
   - Generates monthly actuarial metrics
   - Generates historical metrics over date ranges
   - Supports trends and seasonality in metrics

## Using Enhanced Features

### Initializing with Enhanced Schema

To initialize the database with the enhanced schema:

```bash
# Linux/macOS
./bin/initialize_db.sh --include-enhanced

# Windows
bin\initialize_db.bat --include-enhanced
```

### Running Enhanced Simulation

To run a simulation with enhanced features:

```bash
# Linux/macOS
./bin/run_enhanced_simulation.sh --start-date 2023-01-01 --end-date 2023-01-31 --members-per-day 10

# Windows
bin\run_enhanced_simulation.bat --start-date 2023-01-01 --end-date 2023-01-31 --members-per-day 10
```

### Enhanced Simulation Options

The enhanced simulation supports all options from the standard simulation, plus:

| Option | Description |
|--------|-------------|
| `--fraud-rate` | Rate of fraudulent claims (default: 0.05) |
| `--anomaly-threshold` | Threshold for anomaly detection (default: 0.7) |
| `--financial-detail-level` | Level of financial transaction detail (1-3, default: 2) |
| `--disable-enhanced` | Disable enhanced features |

## Use Cases

### Fraud Detection

The enhanced simulation generates realistic fraud patterns that can be used to test fraud detection algorithms:

1. **Duplicate Claims**: Multiple claims for the same service on the same date
2. **High Frequency Claims**: Unusually high number of claims in a short period
3. **Service Unbundling**: Multiple claims for services that should be bundled
4. **Upcoding**: Using a higher-paying code than the service provided
5. **Phantom Billing**: Billing for services not provided

### Financial Analysis

The enhanced simulation generates detailed financial transactions that can be used for financial analysis:

1. **Premium Payments**: Tracking of premium payments with detailed attributes
2. **Claim Payments**: Tracking of claim payments with processing details
3. **Refunds**: Tracking of refunds and adjustments
4. **Administrative Fees**: Tracking of administrative fees and charges

### Actuarial Analysis

The enhanced simulation generates actuarial metrics that can be used for actuarial analysis:

1. **Loss Ratios**: By age group, gender, state, and product category
2. **Lapse Rates**: By demographic segments and risk profiles
3. **Acquisition Costs**: By age group and product category
4. **Retention Costs**: By age group and product category

## Integration with Data Warehouse

The enhanced schema and data generation are designed to provide a rich source for data warehouse demonstrations:

1. **Fraud Detection Star Schema**: Fact tables for claims with fraud indicators
2. **Financial Analysis Star Schema**: Fact tables for financial transactions
3. **Member Risk Profiling**: Dimension tables for member risk attributes
4. **Provider Analysis**: Dimension tables for provider billing patterns

## Conclusion

The enhanced simulation features provide a more realistic and comprehensive simulation of an Australian health insurance company's operations, particularly for fraud detection, financial analysis, and actuarial metrics. These features can be used to demonstrate data warehouse capabilities and to test analytical algorithms.