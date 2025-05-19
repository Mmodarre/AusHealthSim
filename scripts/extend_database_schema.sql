-- SQL Script to extend existing tables and create new tables for enhanced data generation
-- This script adds risk profile attributes, fraud pattern fields, and billing pattern attributes

-- 1. Extend Insurance.Members with risk profile attributes
ALTER TABLE Insurance.Members
ADD RiskScore DECIMAL(5,2) NULL,
    ChronicConditionFlag BIT DEFAULT 0,
    LifestyleRiskFactor VARCHAR(50) NULL,
    ClaimFrequencyTier VARCHAR(10) NULL,
    PredictedChurn DECIMAL(5,2) NULL;

-- 2. Extend Insurance.Policies with APRA entity codes and risk-adjusted loading
ALTER TABLE Insurance.Policies
ADD APRAEntityCode VARCHAR(10) NULL,
    RiskAdjustedLoading DECIMAL(5,2) NULL,
    UnderwritingScore DECIMAL(5,2) NULL,
    PolicyValueSegment VARCHAR(20) NULL,
    RetentionRiskScore DECIMAL(5,2) NULL;

-- 3. Extend Insurance.Claims with potential fraud pattern fields
ALTER TABLE Insurance.Claims
ADD AnomalyScore DECIMAL(5,2) NULL,
    FraudIndicatorCount INT NULL,
    UnusualPatternFlag BIT DEFAULT 0,
    ClaimComplexityScore DECIMAL(5,2) NULL,
    ClaimAdjustmentHistory VARCHAR(MAX) NULL,
    ReviewFlag BIT DEFAULT 0;

-- 4. Extend Insurance.Providers with billing pattern attributes
ALTER TABLE Insurance.Providers
ADD BillingPatternScore DECIMAL(5,2) NULL,
    AvgClaimValue DECIMAL(9,2) NULL,
    ClaimFrequencyRating VARCHAR(10) NULL,
    SpecialtyRiskFactor DECIMAL(5,2) NULL,
    ComplianceScore DECIMAL(5,2) NULL;

-- 5. Create Insurance.FraudIndicators reference table
CREATE TABLE Insurance.FraudIndicators (
    IndicatorID INT IDENTITY(1,1) PRIMARY KEY,
    IndicatorCode VARCHAR(20) NOT NULL,
    IndicatorName VARCHAR(100) NOT NULL,
    IndicatorDescription VARCHAR(500) NOT NULL,
    SeverityLevel VARCHAR(10) NOT NULL,
    DetectionLogic VARCHAR(MAX) NOT NULL,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    LastModified DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- 6. Create Insurance.FinancialTransactions table
CREATE TABLE Insurance.FinancialTransactions (
    TransactionID INT IDENTITY(1,1) PRIMARY KEY,
    TransactionType VARCHAR(50) NOT NULL,
    TransactionDate DATE NOT NULL,
    Amount DECIMAL(9,2) NOT NULL,
    Description VARCHAR(200) NOT NULL,
    ReferenceNumber VARCHAR(50) NOT NULL,
    RelatedEntityType VARCHAR(20) NOT NULL,
    RelatedEntityID INT NOT NULL,
    ProcessedDate DATETIME2 NOT NULL,
    Status VARCHAR(20) NOT NULL,
    CreatedBy VARCHAR(50) NOT NULL,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    LastModified DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- 7. Create Insurance.ActuarialMetrics reference table
CREATE TABLE Insurance.ActuarialMetrics (
    MetricID INT IDENTITY(1,1) PRIMARY KEY,
    MetricDate DATE NOT NULL,
    MetricType VARCHAR(50) NOT NULL,
    MetricCategory VARCHAR(50) NOT NULL,
    MetricValue DECIMAL(9,4) NOT NULL,
    AgeGroup VARCHAR(20) NULL,
    Gender VARCHAR(10) NULL,
    StateTerritory VARCHAR(3) NULL,
    ProductCategory VARCHAR(50) NULL,
    RiskSegment VARCHAR(20) NULL,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    LastModified DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- 8. Create Insurance.ClaimPatterns table for tracking claim patterns
CREATE TABLE Insurance.ClaimPatterns (
    PatternID INT IDENTITY(1,1) PRIMARY KEY,
    MemberID INT NOT NULL,
    ProviderID INT NOT NULL,
    PatternType VARCHAR(50) NOT NULL,
    PatternDescription VARCHAR(200) NOT NULL,
    FirstDetectedDate DATE NOT NULL,
    LastDetectedDate DATE NOT NULL,
    OccurrenceCount INT NOT NULL,
    AverageAmount DECIMAL(9,2) NOT NULL,
    ConfidenceScore DECIMAL(5,2) NOT NULL,
    Status VARCHAR(20) NOT NULL,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    LastModified DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (MemberID) REFERENCES Insurance.Members(MemberID),
    FOREIGN KEY (ProviderID) REFERENCES Insurance.Providers(ProviderID)
);

-- 9. Populate Insurance.FraudIndicators with initial data
INSERT INTO Insurance.FraudIndicators (IndicatorCode, IndicatorName, IndicatorDescription, SeverityLevel, DetectionLogic)
VALUES
('DUP_CLAIM', 'Duplicate Claim', 'Multiple claims for the same service on the same date', 'High', 'Claims with identical service dates, service descriptions, and member IDs within a 30-day period'),
('FREQ_CLAIM', 'High Frequency Claims', 'Unusually high number of claims in a short period', 'Medium', 'More than 5 claims for the same member within a 30-day period'),
('UNBUNDLING', 'Service Unbundling', 'Multiple claims for services that should be bundled', 'High', 'Multiple related procedure codes submitted separately on the same date'),
('UPCODING', 'Upcoding', 'Using a higher-paying code than the service provided', 'High', 'Consistent pattern of using higher complexity codes than peer average'),
('PHANTOM_BILL', 'Phantom Billing', 'Billing for services not provided', 'Critical', 'Claims for services that conflict with other recorded patient activities'),
('UNUSUAL_MOD', 'Unusual Modifiers', 'Unusual use of modifiers to increase reimbursement', 'Medium', 'Frequent use of modifiers 22, 52, 59 compared to peer average'),
('DISTANT_PAT', 'Distant Patient', 'Patient lives unusually far from provider', 'Low', 'Distance between patient and provider exceeds 100km for routine services'),
('WEEKEND_SERV', 'Weekend Services', 'Unusual pattern of weekend services', 'Low', 'High percentage of services provided on weekends'),
('ROUND_AMOUNT', 'Round Amount Claims', 'Unusually high frequency of round number billing', 'Medium', 'Claims with amounts that are round numbers (ending in 00)'),
('MULTI_DAILY', 'Multiple Daily Visits', 'Multiple visits billed for the same patient on same day', 'Medium', 'More than one visit billed for the same patient on the same day');

-- 10. Populate Insurance.ActuarialMetrics with initial data
INSERT INTO Insurance.ActuarialMetrics (MetricDate, MetricType, MetricCategory, MetricValue, AgeGroup, Gender, StateTerritory, ProductCategory, RiskSegment)
VALUES
('2023-01-01', 'Loss Ratio', 'Hospital', 0.82, '18-30', 'M', 'NSW', 'Gold', 'Low'),
('2023-01-01', 'Loss Ratio', 'Hospital', 0.78, '18-30', 'F', 'NSW', 'Gold', 'Low'),
('2023-01-01', 'Loss Ratio', 'Hospital', 0.85, '31-50', 'M', 'NSW', 'Gold', 'Medium'),
('2023-01-01', 'Loss Ratio', 'Hospital', 0.88, '31-50', 'F', 'NSW', 'Gold', 'Medium'),
('2023-01-01', 'Loss Ratio', 'Hospital', 0.92, '51-70', 'M', 'NSW', 'Gold', 'High'),
('2023-01-01', 'Loss Ratio', 'Hospital', 0.95, '51-70', 'F', 'NSW', 'Gold', 'High'),
('2023-01-01', 'Loss Ratio', 'Hospital', 0.98, '71+', 'M', 'NSW', 'Gold', 'Very High'),
('2023-01-01', 'Loss Ratio', 'Hospital', 0.99, '71+', 'F', 'NSW', 'Gold', 'Very High'),
('2023-01-01', 'Loss Ratio', 'Extras', 0.75, '18-30', 'M', 'NSW', 'Top', 'Low'),
('2023-01-01', 'Loss Ratio', 'Extras', 0.78, '18-30', 'F', 'NSW', 'Top', 'Low'),
('2023-01-01', 'Lapse Rate', 'Hospital', 0.12, '18-30', 'M', 'NSW', 'Gold', 'Low'),
('2023-01-01', 'Lapse Rate', 'Hospital', 0.10, '18-30', 'F', 'NSW', 'Gold', 'Low'),
('2023-01-01', 'Lapse Rate', 'Hospital', 0.08, '31-50', 'M', 'NSW', 'Gold', 'Medium'),
('2023-01-01', 'Lapse Rate', 'Hospital', 0.07, '31-50', 'F', 'NSW', 'Gold', 'Medium'),
('2023-01-01', 'Acquisition Cost', 'Hospital', 320.50, '18-30', NULL, NULL, 'Gold', NULL),
('2023-01-01', 'Acquisition Cost', 'Hospital', 280.75, '31-50', NULL, NULL, 'Gold', NULL),
('2023-01-01', 'Acquisition Cost', 'Hospital', 220.25, '51-70', NULL, NULL, 'Gold', NULL),
('2023-01-01', 'Acquisition Cost', 'Hospital', 180.00, '71+', NULL, NULL, 'Gold', NULL),
('2023-01-01', 'Retention Cost', 'Hospital', 85.50, '18-30', NULL, NULL, 'Gold', NULL),
('2023-01-01', 'Retention Cost', 'Hospital', 65.75, '31-50', NULL, NULL, 'Gold', NULL);