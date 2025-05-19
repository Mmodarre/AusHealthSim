"""
Data models for the Health Insurance AU simulation.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Optional, Any
import json

@dataclass
class Member:
    """Member/Policyholder data model."""
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    address_line1: str
    city: str
    state: str
    post_code: str
    country: str = "Australia"
    member_number: Optional[str] = None
    title: Optional[str] = None
    address_line2: Optional[str] = None
    email: Optional[str] = None
    mobile_phone: Optional[str] = None
    home_phone: Optional[str] = None
    medicare_number: Optional[str] = None
    lhc_loading_percentage: float = 0.0
    phi_rebate_tier: str = "Base"
    join_date: Optional[date] = None
    is_active: bool = True
    # Enhanced attributes for risk profiling
    risk_score: Optional[float] = None
    chronic_condition_flag: bool = False
    lifestyle_risk_factor: Optional[str] = None
    claim_frequency_tier: Optional[str] = None
    predicted_churn: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the member to a dictionary for database operations."""
        return {
            'MemberNumber': self.member_number,
            'Title': self.title,
            'FirstName': self.first_name,
            'LastName': self.last_name,
            'DateOfBirth': self.date_of_birth,
            'Gender': self.gender,
            'Email': self.email,
            'MobilePhone': self.mobile_phone,
            'HomePhone': self.home_phone,
            'AddressLine1': self.address_line1,
            'AddressLine2': self.address_line2,
            'City': self.city,
            'State': self.state,
            'PostCode': self.post_code,
            'Country': self.country,
            'MedicareNumber': self.medicare_number,
            'LHCLoadingPercentage': self.lhc_loading_percentage,
            'PHIRebateTier': self.phi_rebate_tier,
            'JoinDate': self.join_date or datetime.now().date(),
            'IsActive': self.is_active,
            'RiskScore': self.risk_score,
            'ChronicConditionFlag': self.chronic_condition_flag,
            'LifestyleRiskFactor': self.lifestyle_risk_factor,
            'ClaimFrequencyTier': self.claim_frequency_tier,
            'PredictedChurn': self.predicted_churn
        }

@dataclass
class CoveragePlan:
    """Health insurance coverage plan data model."""
    plan_code: str
    plan_name: str
    plan_type: str  # Hospital, Extras, Combined
    monthly_premium: float
    annual_premium: float
    effective_date: date
    hospital_tier: Optional[str] = None  # Basic, Bronze, Silver, Gold
    excess_options: List[float] = field(default_factory=list)
    waiting_periods: Dict[str, int] = field(default_factory=dict)
    coverage_details: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    end_date: Optional[date] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the coverage plan to a dictionary for database operations."""
        return {
            'PlanCode': self.plan_code,
            'PlanName': self.plan_name,
            'PlanType': self.plan_type,
            'HospitalTier': self.hospital_tier,
            'MonthlyPremium': self.monthly_premium,
            'AnnualPremium': self.annual_premium,
            'ExcessOptions': json.dumps(self.excess_options) if self.excess_options else None,
            'WaitingPeriods': json.dumps(self.waiting_periods) if self.waiting_periods else None,
            'CoverageDetails': json.dumps(self.coverage_details) if self.coverage_details else None,
            'IsActive': self.is_active,
            'EffectiveDate': self.effective_date,
            'EndDate': self.end_date
        }

@dataclass
class Policy:
    """Health insurance policy data model."""
    policy_number: str
    primary_member_id: int
    plan_id: int
    coverage_type: str  # Single, Couple, Family, Single Parent
    start_date: date
    current_premium: float
    premium_frequency: str = "Monthly"  # Monthly, Quarterly, Annually
    excess_amount: float = 0.0
    rebate_percentage: float = 0.0
    lhc_loading_percentage: float = 0.0
    status: str = "Active"  # Active, Suspended, Cancelled, Lapsed
    payment_method: str = "Direct Debit"
    end_date: Optional[date] = None
    last_premium_paid_date: Optional[date] = None
    next_premium_due_date: Optional[date] = None
    # Enhanced attributes for risk-adjusted loading
    apra_entity_code: Optional[str] = None
    risk_adjusted_loading: Optional[float] = None
    underwriting_score: Optional[float] = None
    policy_value_segment: Optional[str] = None
    retention_risk_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the policy to a dictionary for database operations."""
        return {
            'PolicyNumber': self.policy_number,
            'PrimaryMemberID': self.primary_member_id,
            'PlanID': self.plan_id,
            'CoverageType': self.coverage_type,
            'StartDate': self.start_date,
            'EndDate': self.end_date,
            'ExcessAmount': self.excess_amount,
            'PremiumFrequency': self.premium_frequency,
            'CurrentPremium': self.current_premium,
            'RebatePercentage': self.rebate_percentage,
            'LHCLoadingPercentage': self.lhc_loading_percentage,
            'Status': self.status,
            'PaymentMethod': self.payment_method,
            'LastPremiumPaidDate': self.last_premium_paid_date,
            'NextPremiumDueDate': self.next_premium_due_date,
            'APRAEntityCode': self.apra_entity_code,
            'RiskAdjustedLoading': self.risk_adjusted_loading,
            'UnderwritingScore': self.underwriting_score,
            'PolicyValueSegment': self.policy_value_segment,
            'RetentionRiskScore': self.retention_risk_score
        }

@dataclass
class PolicyMember:
    """Policy member relationship data model."""
    policy_id: int
    member_id: int
    relationship_to_primary: str  # Self, Spouse, Child, Dependent
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the policy member to a dictionary for database operations."""
        return {
            'PolicyID': self.policy_id,
            'MemberID': self.member_id,
            'RelationshipToPrimary': self.relationship_to_primary,
            'StartDate': self.start_date,
            'EndDate': self.end_date,
            'IsActive': self.is_active
        }

@dataclass
class Provider:
    """Healthcare provider data model."""
    provider_number: str
    provider_name: str
    provider_type: str
    address_line1: str
    city: str
    state: str
    post_code: str
    country: str = "Australia"
    address_line2: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_preferred_provider: bool = False
    agreement_start_date: Optional[date] = None
    agreement_end_date: Optional[date] = None
    is_active: bool = True
    # Enhanced attributes for billing pattern analysis
    billing_pattern_score: Optional[float] = None
    avg_claim_value: Optional[float] = None
    claim_frequency_rating: Optional[str] = None
    specialty_risk_factor: Optional[float] = None
    compliance_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the provider to a dictionary for database operations."""
        return {
            'ProviderNumber': self.provider_number,
            'ProviderName': self.provider_name,
            'ProviderType': self.provider_type,
            'AddressLine1': self.address_line1,
            'AddressLine2': self.address_line2,
            'City': self.city,
            'State': self.state,
            'PostCode': self.post_code,
            'Country': self.country,
            'Phone': self.phone,
            'Email': self.email,
            'IsPreferredProvider': self.is_preferred_provider,
            'AgreementStartDate': self.agreement_start_date,
            'AgreementEndDate': self.agreement_end_date,
            'IsActive': self.is_active,
            'BillingPatternScore': self.billing_pattern_score,
            'AvgClaimValue': self.avg_claim_value,
            'ClaimFrequencyRating': self.claim_frequency_rating,
            'SpecialtyRiskFactor': self.specialty_risk_factor,
            'ComplianceScore': self.compliance_score
        }

@dataclass
class Claim:
    """Health insurance claim data model."""
    claim_number: str
    policy_id: int
    member_id: int
    provider_id: int
    service_date: datetime  # Changed from date to datetime
    submission_date: datetime  # Changed from date to datetime
    claim_type: str
    service_description: str
    charged_amount: float
    medicare_amount: float = 0.0
    insurance_amount: float = 0.0
    gap_amount: float = 0.0
    excess_applied: float = 0.0
    mbs_item_number: Optional[str] = None
    status: str = "Submitted"  # Submitted, In Process, Approved, Paid, Rejected
    processed_date: Optional[datetime] = None  # Changed from date to datetime
    payment_date: Optional[datetime] = None  # Changed from date to datetime
    rejection_reason: Optional[str] = None
    # Enhanced attributes for fraud detection
    anomaly_score: Optional[float] = None
    fraud_indicator_count: Optional[int] = None
    unusual_pattern_flag: bool = False
    claim_complexity_score: Optional[float] = None
    claim_adjustment_history: Optional[str] = None
    review_flag: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the claim to a dictionary for database operations."""
        return {
            'ClaimNumber': self.claim_number,
            'PolicyID': self.policy_id,
            'MemberID': self.member_id,
            'ProviderID': self.provider_id,
            'ServiceDate': self.service_date,
            'SubmissionDate': self.submission_date,
            'ClaimType': self.claim_type,
            'ServiceDescription': self.service_description,
            'MBSItemNumber': self.mbs_item_number,
            'ChargedAmount': self.charged_amount,
            'MedicareAmount': self.medicare_amount,
            'InsuranceAmount': self.insurance_amount,
            'GapAmount': self.gap_amount,
            'ExcessApplied': self.excess_applied,
            'Status': self.status,
            'ProcessedDate': self.processed_date,
            'PaymentDate': self.payment_date,
            'RejectionReason': self.rejection_reason,
            'AnomalyScore': self.anomaly_score,
            'FraudIndicatorCount': self.fraud_indicator_count,
            'UnusualPatternFlag': self.unusual_pattern_flag,
            'ClaimComplexityScore': self.claim_complexity_score,
            'ClaimAdjustmentHistory': self.claim_adjustment_history,
            'ReviewFlag': self.review_flag
        }

@dataclass
class PremiumPayment:
    """Premium payment data model."""
    policy_id: int
    payment_date: date
    payment_amount: float
    payment_method: str
    period_start_date: date
    period_end_date: date
    payment_reference: Optional[str] = None
    payment_status: str = "Successful"  # Successful, Failed, Pending, Refunded
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the premium payment to a dictionary for database operations."""
        return {
            'PolicyID': self.policy_id,
            'PaymentDate': self.payment_date,
            'PaymentAmount': self.payment_amount,
            'PaymentMethod': self.payment_method,
            'PaymentReference': self.payment_reference,
            'PaymentStatus': self.payment_status,
            'PeriodStartDate': self.period_start_date,
            'PeriodEndDate': self.period_end_date
        }

@dataclass
class FraudIndicator:
    """Fraud indicator reference data model."""
    indicator_code: str
    indicator_name: str
    indicator_description: str
    severity_level: str
    detection_logic: str
    indicator_id: Optional[int] = None
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the fraud indicator to a dictionary for database operations."""
        return {
            'IndicatorCode': self.indicator_code,
            'IndicatorName': self.indicator_name,
            'IndicatorDescription': self.indicator_description,
            'SeverityLevel': self.severity_level,
            'DetectionLogic': self.detection_logic,
            'CreatedDate': self.created_date or datetime.now(),
            'LastModified': self.last_modified or datetime.now()
        }

@dataclass
class FinancialTransaction:
    """Financial transaction data model."""
    transaction_type: str
    transaction_date: date
    amount: float
    description: str
    reference_number: str
    related_entity_type: str
    related_entity_id: int
    processed_date: datetime
    status: str
    created_by: str
    transaction_id: Optional[int] = None
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the financial transaction to a dictionary for database operations."""
        return {
            'TransactionType': self.transaction_type,
            'TransactionDate': self.transaction_date,
            'Amount': self.amount,
            'Description': self.description,
            'ReferenceNumber': self.reference_number,
            'RelatedEntityType': self.related_entity_type,
            'RelatedEntityID': self.related_entity_id,
            'ProcessedDate': self.processed_date,
            'Status': self.status,
            'CreatedBy': self.created_by,
            'CreatedDate': self.created_date or datetime.now(),
            'LastModified': self.last_modified or datetime.now()
        }

@dataclass
class ActuarialMetric:
    """Actuarial metric reference data model."""
    metric_date: date
    metric_type: str
    metric_category: str
    metric_value: float
    metric_id: Optional[int] = None
    age_group: Optional[str] = None
    gender: Optional[str] = None
    state_territory: Optional[str] = None
    product_category: Optional[str] = None
    risk_segment: Optional[str] = None
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the actuarial metric to a dictionary for database operations."""
        return {
            'MetricDate': self.metric_date,
            'MetricType': self.metric_type,
            'MetricCategory': self.metric_category,
            'MetricValue': self.metric_value,
            'AgeGroup': self.age_group,
            'Gender': self.gender,
            'StateTerritory': self.state_territory,
            'ProductCategory': self.product_category,
            'RiskSegment': self.risk_segment,
            'CreatedDate': self.created_date or datetime.now(),
            'LastModified': self.last_modified or datetime.now()
        }

@dataclass
class ClaimPattern:
    """Claim pattern data model for tracking claim patterns."""
    member_id: int
    provider_id: int
    pattern_type: str
    pattern_description: str
    first_detected_date: date
    last_detected_date: date
    occurrence_count: int
    average_amount: float
    confidence_score: float
    status: str
    pattern_id: Optional[int] = None
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the claim pattern to a dictionary for database operations."""
        return {
            'MemberID': self.member_id,
            'ProviderID': self.provider_id,
            'PatternType': self.pattern_type,
            'PatternDescription': self.pattern_description,
            'FirstDetectedDate': self.first_detected_date,
            'LastDetectedDate': self.last_detected_date,
            'OccurrenceCount': self.occurrence_count,
            'AverageAmount': self.average_amount,
            'ConfidenceScore': self.confidence_score,
            'Status': self.status,
            'CreatedDate': self.created_date or datetime.now(),
            'LastModified': self.last_modified or datetime.now()
        }