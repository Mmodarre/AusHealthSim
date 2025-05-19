"""
Simulation orchestrator for enhanced data generation.
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from health_insurance_au.data_generation.fraud_patterns import FraudPatternGenerator
from health_insurance_au.data_generation.financial_transactions import FinancialTransactionGenerator
from health_insurance_au.data_generation.provider_billing import ProviderBillingGenerator
from health_insurance_au.data_generation.claim_patterns import ClaimPatternGenerator
from health_insurance_au.data_generation.actuarial_data import ActuarialDataGenerator
from health_insurance_au.models.models import (
    Member, Provider, Claim, Policy, ActuarialMetric, 
    FinancialTransaction, ClaimPattern
)
from health_insurance_au.utils.db_utils import execute_query
from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

class SimulationOrchestrator:
    """
    Class for coordinating all data generation activities.
    """
    
    def __init__(self):
        """Initialize the simulation orchestrator."""
        self.fraud_generator = FraudPatternGenerator()
        self.financial_generator = FinancialTransactionGenerator()
        self.provider_billing_generator = ProviderBillingGenerator()
        self.claim_pattern_generator = ClaimPatternGenerator()
        self.actuarial_generator = ActuarialDataGenerator()
    
    def load_members(self) -> List[Member]:
        """
        Load members from the database.
        
        Returns:
            A list of Member objects
        """
        try:
            members_data = execute_query("SELECT * FROM Insurance.Members")
            members = []
            
            for data in members_data:
                member = Member(
                    member_number=data['MemberNumber'],
                    first_name=data['FirstName'],
                    last_name=data['LastName'],
                    date_of_birth=data['DateOfBirth'],
                    gender=data['Gender'],
                    address_line1=data['AddressLine1'],
                    city=data['City'],
                    state=data['State'],
                    post_code=data['PostCode'],
                    country=data['Country'],
                    title=data['Title'],
                    address_line2=data['AddressLine2'],
                    email=data['Email'],
                    mobile_phone=data['MobilePhone'],
                    home_phone=data['HomePhone'],
                    medicare_number=data['MedicareNumber'],
                    lhc_loading_percentage=float(data['LHCLoadingPercentage']) if data['LHCLoadingPercentage'] else 0.0,
                    phi_rebate_tier=data['PHIRebateTier'],
                    join_date=data['JoinDate'],
                    is_active=data['IsActive']
                )
                # Store the member ID for reference
                setattr(member, 'member_id', data['MemberID'])
                members.append(member)
            
            logger.info(f"Loaded {len(members)} members from database")
            return members
        except Exception as e:
            logger.error(f"Error loading members: {e}")
            return []
    
    def load_providers(self) -> List[Provider]:
        """
        Load providers from the database.
        
        Returns:
            A list of Provider objects
        """
        try:
            providers_data = execute_query("SELECT * FROM Insurance.Providers")
            providers = []
            
            for data in providers_data:
                provider = Provider(
                    provider_number=data['ProviderNumber'],
                    provider_name=data['ProviderName'],
                    provider_type=data['ProviderType'],
                    address_line1=data['AddressLine1'],
                    city=data['City'],
                    state=data['State'],
                    post_code=data['PostCode'],
                    country=data['Country'],
                    address_line2=data['AddressLine2'],
                    phone=data['Phone'],
                    email=data['Email'],
                    is_preferred_provider=data['IsPreferredProvider'],
                    agreement_start_date=data['AgreementStartDate'],
                    agreement_end_date=data['AgreementEndDate'],
                    is_active=data['IsActive']
                )
                # Store the provider ID for reference
                setattr(provider, 'provider_id', data['ProviderID'])
                providers.append(provider)
            
            logger.info(f"Loaded {len(providers)} providers from database")
            return providers
        except Exception as e:
            logger.error(f"Error loading providers: {e}")
            return []
    
    def load_policies(self) -> List[Policy]:
        """
        Load policies from the database.
        
        Returns:
            A list of Policy objects
        """
        try:
            policies_data = execute_query("SELECT * FROM Insurance.Policies")
            policies = []
            
            for data in policies_data:
                policy = Policy(
                    policy_number=data['PolicyNumber'],
                    primary_member_id=data['PrimaryMemberID'],
                    plan_id=data['PlanID'],
                    coverage_type=data['CoverageType'],
                    start_date=data['StartDate'],
                    current_premium=float(data['CurrentPremium']),
                    premium_frequency=data['PremiumFrequency'],
                    excess_amount=float(data['ExcessAmount']),
                    rebate_percentage=float(data['RebatePercentage']),
                    lhc_loading_percentage=float(data['LHCLoadingPercentage']),
                    status=data['Status'],
                    payment_method=data['PaymentMethod'],
                    end_date=data['EndDate'],
                    last_premium_paid_date=data['LastPremiumPaidDate'],
                    next_premium_due_date=data['NextPremiumDueDate']
                )
                # Store the policy ID for reference
                setattr(policy, 'policy_id', data['PolicyID'])
                policies.append(policy)
            
            logger.info(f"Loaded {len(policies)} policies from database")
            return policies
        except Exception as e:
            logger.error(f"Error loading policies: {e}")
            return []
    
    def load_claims(self) -> List[Claim]:
        """
        Load claims from the database.
        
        Returns:
            A list of Claim objects
        """
        try:
            claims_data = execute_query("SELECT * FROM Insurance.Claims")
            claims = []
            
            for data in claims_data:
                claim = Claim(
                    claim_number=data['ClaimNumber'],
                    policy_id=data['PolicyID'],
                    member_id=data['MemberID'],
                    provider_id=data['ProviderID'],
                    service_date=data['ServiceDate'],
                    submission_date=data['SubmissionDate'],
                    claim_type=data['ClaimType'],
                    service_description=data['ServiceDescription'],
                    charged_amount=float(data['ChargedAmount']),
                    medicare_amount=float(data['MedicareAmount']),
                    insurance_amount=float(data['InsuranceAmount']),
                    gap_amount=float(data['GapAmount']),
                    excess_applied=float(data['ExcessApplied']),
                    mbs_item_number=data['MBSItemNumber'],
                    status=data['Status'],
                    processed_date=data['ProcessedDate'],
                    payment_date=data['PaymentDate'],
                    rejection_reason=data['RejectionReason']
                )
                # Store the claim ID for reference
                setattr(claim, 'claim_id', data['ClaimID'])
                claims.append(claim)
            
            logger.info(f"Loaded {len(claims)} claims from database")
            return claims
        except Exception as e:
            logger.error(f"Error loading claims: {e}")
            return []
    
    def generate_member_risk_profiles(self, members: List[Member], simulation_date: date = None) -> int:
        """
        Generate risk profiles for members.
        
        Args:
            members: List of members to generate profiles for
            simulation_date: The simulation date
            
        Returns:
            Number of members updated
        """
        if simulation_date is None:
            simulation_date = date.today()
        
        updated_count = 0
        
        for member in members:
            # Generate risk profile attributes
            member.risk_score = round(random.uniform(0.1, 5.0), 2)
            member.chronic_condition_flag = random.random() < 0.15  # 15% have chronic conditions
            
            lifestyle_factors = ['Smoker', 'Sedentary', 'Active', 'Athletic', 'High BMI', 'Normal BMI', 'Low BMI']
            member.lifestyle_risk_factor = random.choice(lifestyle_factors)
            
            claim_tiers = ['Low', 'Medium', 'High', 'Very High']
            member.claim_frequency_tier = random.choice(claim_tiers)
            
            member.predicted_churn = round(random.uniform(0.01, 0.5), 2)
            
            # Update in database
            member_id = getattr(member, 'member_id', 0)
            if member_id == 0:
                continue
                
            try:
                query = """
                UPDATE Insurance.Members
                SET RiskScore = ?, ChronicConditionFlag = ?, LifestyleRiskFactor = ?,
                    ClaimFrequencyTier = ?, PredictedChurn = ?, LastModified = ?
                WHERE MemberID = ?
                """
                execute_non_query(query, (
                    member.risk_score,
                    member.chronic_condition_flag,
                    member.lifestyle_risk_factor,
                    member.claim_frequency_tier,
                    member.predicted_churn,
                    simulation_date,
                    member_id
                ), simulation_date)
                
                updated_count += 1
            except Exception as e:
                logger.error(f"Error updating member {member_id} risk profile: {e}")
        
        logger.info(f"Updated risk profiles for {updated_count} members")
        return updated_count
    
    def generate_policy_risk_attributes(self, policies: List[Policy], simulation_date: date = None) -> int:
        """
        Generate risk attributes for policies.
        
        Args:
            policies: List of policies to generate attributes for
            simulation_date: The simulation date
            
        Returns:
            Number of policies updated
        """
        if simulation_date is None:
            simulation_date = date.today()
        
        updated_count = 0
        
        # APRA entity codes
        apra_entity_codes = ['HEA001', 'HEA002', 'HEA003', 'HEA004', 'HEA005']
        
        # Policy value segments
        value_segments = ['Low Value', 'Standard', 'High Value', 'Premium']
        
        for policy in policies:
            # Generate risk attributes
            policy.apra_entity_code = random.choice(apra_entity_codes)
            policy.risk_adjusted_loading = round(random.uniform(0.0, 0.25), 2)
            policy.underwriting_score = round(random.uniform(0.3, 0.95), 2)
            policy.policy_value_segment = random.choice(value_segments)
            policy.retention_risk_score = round(random.uniform(0.1, 0.9), 2)
            
            # Update in database
            policy_id = getattr(policy, 'policy_id', 0)
            if policy_id == 0:
                continue
                
            try:
                query = """
                UPDATE Insurance.Policies
                SET APRAEntityCode = ?, RiskAdjustedLoading = ?, UnderwritingScore = ?,
                    PolicyValueSegment = ?, RetentionRiskScore = ?, LastModified = ?
                WHERE PolicyID = ?
                """
                execute_non_query(query, (
                    policy.apra_entity_code,
                    policy.risk_adjusted_loading,
                    policy.underwriting_score,
                    policy.policy_value_segment,
                    policy.retention_risk_score,
                    simulation_date,
                    policy_id
                ), simulation_date)
                
                updated_count += 1
            except Exception as e:
                logger.error(f"Error updating policy {policy_id} risk attributes: {e}")
        
        logger.info(f"Updated risk attributes for {updated_count} policies")
        return updated_count
    
    def run_enhanced_simulation(self, simulation_date: date = None, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a complete enhanced simulation.
        
        Args:
            simulation_date: The date to simulate
            config: Configuration dictionary with simulation parameters
            
        Returns:
            A dictionary with simulation results
        """
        if simulation_date is None:
            simulation_date = date.today()
            
        # Default configuration
        default_config = {
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
        
        # Use provided config or default
        config = config or default_config
        
        # Results dictionary
        results = {
            'simulation_date': simulation_date,
            'members_updated': 0,
            'policies_updated': 0,
            'providers_updated': 0,
            'claims_updated': 0,
            'claim_patterns_generated': 0,
            'financial_transactions_generated': 0,
            'actuarial_metrics_generated': 0
        }
        
        # Load data
        members = self.load_members()
        providers = self.load_providers()
        policies = self.load_policies()
        claims = self.load_claims()
        
        # Generate member risk profiles
        if config.get('generate_member_risk_profiles', True):
            results['members_updated'] = self.generate_member_risk_profiles(members, simulation_date)
        
        # Generate policy risk attributes
        if config.get('generate_policy_risk_attributes', True):
            results['policies_updated'] = self.generate_policy_risk_attributes(policies, simulation_date)
        
        # Generate provider billing attributes
        if config.get('generate_provider_billing_attributes', True):
            providers = self.provider_billing_generator.generate_provider_billing_attributes(providers, claims)
            results['providers_updated'] = self.provider_billing_generator.update_provider_billing_attributes(providers, simulation_date)
        
        # Apply fraud patterns to claims
        if config.get('apply_fraud_patterns', True):
            claims = self.fraud_generator.apply_fraud_patterns_to_claims(claims, simulation_date)
            # Update claims in database would go here
            results['claims_updated'] = len(claims)
        
        # Generate claim patterns
        if config.get('generate_claim_patterns', True):
            member_ids = [getattr(m, 'member_id', 0) for m in members if getattr(m, 'member_id', 0) > 0]
            provider_ids = [getattr(p, 'provider_id', 0) for p in providers if getattr(p, 'provider_id', 0) > 0]
            
            if member_ids and provider_ids:
                claim_patterns = self.fraud_generator.generate_claim_patterns(member_ids, provider_ids, simulation_date)
                results['claim_patterns_generated'] = self.fraud_generator.save_claim_patterns(claim_patterns, simulation_date)
        
        # Generate financial transactions
        if config.get('generate_financial_transactions', True):
            # Premium transactions
            premium_transactions = self.financial_generator.generate_premium_transactions(policies, simulation_date)
            
            # Claim payment transactions
            claim_payment_transactions = self.financial_generator.generate_claim_payment_transactions(claims, simulation_date)
            
            # Miscellaneous transactions
            misc_count = config.get('financial_transaction_count', 30) - len(premium_transactions) - len(claim_payment_transactions)
            misc_count = max(0, misc_count)
            misc_transactions = self.financial_generator.generate_miscellaneous_transactions(policies, simulation_date, misc_count)
            
            # Combine all transactions
            all_transactions = premium_transactions + claim_payment_transactions + misc_transactions
            
            # Save transactions
            results['financial_transactions_generated'] = self.financial_generator.save_transactions(all_transactions, simulation_date)
        
        # Generate actuarial metrics
        if config.get('generate_actuarial_metrics', True):
            metrics_count = config.get('actuarial_metrics_count', 50)
            actuarial_metrics = self.actuarial_generator.generate_monthly_metrics(simulation_date, metrics_count)
            results['actuarial_metrics_generated'] = self.actuarial_generator.save_metrics(actuarial_metrics, simulation_date)
        
        logger.info(f"Enhanced simulation completed for {simulation_date}")
        return results