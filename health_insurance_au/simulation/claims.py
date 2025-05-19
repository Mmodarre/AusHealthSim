"""
Claims generator for the Health Insurance AU simulation.
"""
import random
import string
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from health_insurance_au.config import CLAIM_TYPES
from health_insurance_au.models.models import Claim, Policy, Member, Provider
from health_insurance_au.utils.logging_config import get_logger
from health_insurance_au.utils.datetime_utils import generate_random_datetime
from health_insurance_au.utils.db_utils import execute_query, execute_non_query

# Set up logging
logger = get_logger(__name__)

# MBS item numbers and descriptions for hospital claims
HOSPITAL_MBS_ITEMS = [
    {'number': '30390', 'description': 'Appendicectomy', 'fee': 445.40},
    {'number': '49318', 'description': 'Knee arthroscopy', 'fee': 379.75},
    {'number': '49569', 'description': 'Knee replacement', 'fee': 1317.80},
    {'number': '39000', 'description': 'Brain tumor removal', 'fee': 1586.75},
    {'number': '30535', 'description': 'Hernia repair', 'fee': 464.50},
    {'number': '47516', 'description': 'Fracture treatment', 'fee': 385.50},
    {'number': '41789', 'description': 'Tonsillectomy', 'fee': 295.70},
    {'number': '30571', 'description': 'Cholecystectomy', 'fee': 741.90},
    {'number': '16520', 'description': 'Caesarean section', 'fee': 693.95},
    {'number': '30473', 'description': 'Breast biopsy', 'fee': 260.05}
]

# Service descriptions for general treatment claims
GENERAL_TREATMENT_SERVICES = {
    'Dental': [
        {'description': 'Dental checkup and clean', 'fee': 120.00},
        {'description': 'Dental filling', 'fee': 150.00},
        {'description': 'Root canal treatment', 'fee': 350.00},
        {'description': 'Tooth extraction', 'fee': 180.00},
        {'description': 'Dental crown', 'fee': 1200.00}
    ],
    'Optical': [
        {'description': 'Eye examination', 'fee': 80.00},
        {'description': 'Single vision glasses', 'fee': 250.00},
        {'description': 'Multifocal glasses', 'fee': 450.00},
        {'description': 'Contact lenses', 'fee': 200.00}
    ],
    'Physiotherapy': [
        {'description': 'Initial physiotherapy consultation', 'fee': 90.00},
        {'description': 'Follow-up physiotherapy session', 'fee': 75.00},
        {'description': 'Extended physiotherapy treatment', 'fee': 120.00}
    ],
    'Chiropractic': [
        {'description': 'Initial chiropractic consultation', 'fee': 85.00},
        {'description': 'Chiropractic adjustment', 'fee': 65.00},
        {'description': 'Spinal assessment', 'fee': 95.00}
    ],
    'Psychology': [
        {'description': 'Initial psychology consultation', 'fee': 180.00},
        {'description': 'Psychology session', 'fee': 150.00},
        {'description': 'Extended psychology session', 'fee': 220.00}
    ],
    'Podiatry': [
        {'description': 'Podiatry consultation', 'fee': 85.00},
        {'description': 'Custom orthotics', 'fee': 350.00},
        {'description': 'Nail surgery', 'fee': 250.00}
    ],
    'Acupuncture': [
        {'description': 'Acupuncture session', 'fee': 75.00},
        {'description': 'Extended acupuncture treatment', 'fee': 95.00}
    ],
    'Naturopathy': [
        {'description': 'Naturopathy consultation', 'fee': 90.00},
        {'description': 'Follow-up naturopathy session', 'fee': 70.00}
    ],
    'Remedial Massage': [
        {'description': '30-minute massage', 'fee': 60.00},
        {'description': '60-minute massage', 'fee': 90.00},
        {'description': '90-minute massage', 'fee': 130.00}
    ],
    'Ambulance': [
        {'description': 'Emergency ambulance service', 'fee': 425.00},
        {'description': 'Non-emergency ambulance transport', 'fee': 250.00}
    ]
}

def generate_claim_number(simulation_date: date = None) -> str:
    """
    Generate a random claim number.
    
    Args:
        simulation_date: The date to use in the claim number (default: today)
    
    Returns:
        A claim number in the format CLM-YYYYMMDD-NNNNN
    """
    # Format: CLM-YYYYMMDD-NNNNN where YYYYMMDD is the simulation date and NNNNN is a 5-digit number
    date_str = simulation_date.strftime('%Y%m%d') if simulation_date else date.today().strftime('%Y%m%d')
    number = ''.join(random.choices(string.digits, k=5)).zfill(5)  # Ensure 5 digits
    return f"CLM-{date_str}-{number} "  # Added space to make it 19 characters

def generate_hospital_claims(
    policies: List[Policy], 
    members: List[Member], 
    providers: List[Provider], 
    count: int = 5,
    simulation_date: date = None
) -> List[Claim]:
    """
    Generate hospital claims.
    
    Args:
        policies: List of policies
        members: List of members
        providers: List of providers
        count: Number of claims to generate
        simulation_date: The date to use for claim generation (default: today)
        
    Returns:
        A list of Claim objects
    """
    claims = []
    
    if simulation_date is None:
        simulation_date = date.today()
    
    # Filter for active policies
    active_policies = [p for p in policies if p.status == 'Active']
    if not active_policies:
        logger.warning("No active policies available to generate claims")
        return claims
    
    # Check if members list is empty
    if not members:
        logger.warning("No members available to generate claims")
        return claims
    
    # Filter for hospital providers
    hospital_providers = [p for p in providers if p.provider_type == 'Hospital']
    if not hospital_providers:
        logger.warning("No hospital providers available to generate claims")
        return claims
    
    for i in range(count):
        # Select a random policy
        policy = random.choice(active_policies)
        
        # Select a member from this policy (assuming policy_members is not available here)
        # In a real implementation, we would use policy_members to get valid members for each policy
        member_id = policy.primary_member_id
        
        # Select a hospital provider
        provider = random.choice(hospital_providers)
        
        # Select an MBS item
        mbs_item = random.choice(HOSPITAL_MBS_ITEMS)
        
        # Generate service date (within the last 90 days from simulation date)
        service_date_date = simulation_date - timedelta(days=random.randint(1, 90))
        service_date = generate_random_datetime(service_date_date)
        
        # Generate submission date (a few days after service date, but not after simulation date)
        days_after_service = random.randint(1, 10)
        submission_date_date = min(service_date_date + timedelta(days=days_after_service), simulation_date)
        submission_date = generate_random_datetime(submission_date_date)
        
        # Calculate charged amount (MBS fee plus a markup)
        markup = random.uniform(1.5, 3.0)
        charged_amount = round(mbs_item['fee'] * markup, 2)
        
        # Calculate Medicare amount (75% of MBS fee for inpatient services)
        medicare_amount = round(mbs_item['fee'] * 0.75, 2)
        
        # Determine if excess should be applied
        excess_applied = 0.0
        if random.random() < 0.3:  # 30% chance of applying excess
            excess_applied = min(policy.excess_amount, charged_amount - medicare_amount)
        
        # Calculate insurance amount (remaining after Medicare and excess)
        insurance_amount = round(charged_amount - medicare_amount - excess_applied, 2)
        
        # Calculate gap amount (if any)
        gap_amount = max(0, round(charged_amount - medicare_amount - insurance_amount - excess_applied, 2))
        
        # Generate claim number
        claim_number = generate_claim_number(simulation_date)
        
        # Determine claim status
        status = random.choices(
            ['Submitted', 'In Process', 'Approved', 'Paid', 'Rejected'],
            weights=[0.1, 0.1, 0.2, 0.5, 0.1],
            k=1
        )[0]
        
        # Generate processed date and payment date if applicable
        processed_date = None
        payment_date = None
        rejection_reason = None
        
        if status in ['Approved', 'Paid']:
            # Processed date should be between submission date and simulation date
            max_days_after_submission = max(0, (simulation_date - submission_date_date).days)
            if max_days_after_submission > 0:
                days_after_submission = random.randint(1, min(14, max_days_after_submission))
                processed_date_date = submission_date_date + timedelta(days=days_after_submission)
                processed_date = generate_random_datetime(processed_date_date)
                
                if status == 'Paid' and processed_date_date < simulation_date:
                    # Payment date should be between processed date and simulation date
                    max_days_after_processed = max(0, (simulation_date - processed_date_date).days)
                    if max_days_after_processed > 0:
                        days_after_processed = random.randint(1, min(7, max_days_after_processed))
                        payment_date_date = processed_date_date + timedelta(days=days_after_processed)
                        payment_date = generate_random_datetime(payment_date_date)
        elif status == 'Rejected':
            # Processed date should be between submission date and simulation date
            max_days_after_submission = max(0, (simulation_date - submission_date_date).days)
            if max_days_after_submission > 0:
                days_after_submission = random.randint(1, min(14, max_days_after_submission))
                processed_date_date = submission_date_date + timedelta(days=days_after_submission)
                processed_date = generate_random_datetime(processed_date_date)
            
            rejection_reasons = [
                'Service not covered by policy',
                'Waiting period not served',
                'Insufficient documentation',
                'Duplicate claim',
                'Member not covered on service date'
            ]
            rejection_reason = random.choice(rejection_reasons)
        
        # Create the claim
        claim = Claim(
            claim_number=claim_number,
            policy_id=policies.index(policy) + 1,  # Assuming PolicyID starts at 1
            member_id=member_id,
            provider_id=providers.index(provider) + 1,  # Assuming ProviderID starts at 1
            service_date=service_date,
            submission_date=submission_date,
            claim_type='Hospital',
            service_description=mbs_item['description'],
            mbs_item_number=mbs_item['number'],
            charged_amount=charged_amount,
            medicare_amount=medicare_amount,
            insurance_amount=insurance_amount,
            gap_amount=gap_amount,
            excess_applied=excess_applied,
            status=status,
            processed_date=processed_date,
            payment_date=payment_date,
            rejection_reason=rejection_reason
        )
        
        claims.append(claim)
    
    logger.info(f"Generated {len(claims)} hospital claims")
    return claims

def generate_general_treatment_claims(
    policies: List[Policy], 
    members: List[Member], 
    providers: List[Provider], 
    count: int = 15,
    simulation_date: date = None
) -> List[Claim]:
    """
    Generate general treatment claims (dental, optical, etc.).
    
    Args:
        policies: List of policies
        members: List of members
        providers: List of providers
        count: Number of claims to generate
        simulation_date: The date to use for claim generation (default: today)
        
    Returns:
        A list of Claim objects
    """
    claims = []
    
    if simulation_date is None:
        simulation_date = date.today()
    
    # Filter for active policies
    active_policies = [p for p in policies if p.status == 'Active']
    if not active_policies:
        logger.warning("No active policies available to generate claims")
        return claims
    
    # Check if members list is empty
    if not members:
        logger.warning("No members available to generate claims")
        return claims
    
    # Filter out hospital providers
    general_providers = [p for p in providers if p.provider_type != 'Hospital']
    if not general_providers:
        logger.warning("No general treatment providers available to generate claims")
        return claims
    
    for i in range(count):
        # Select a random policy
        policy = random.choice(active_policies)
        
        # Select a member from this policy (assuming policy_members is not available here)
        # In a real implementation, we would use policy_members to get valid members for each policy
        member_id = policy.primary_member_id
        
        # Select a claim type
        claim_type = random.choice([t for t in CLAIM_TYPES if t != 'Hospital' and t != 'Medical'])
        
        # Select a provider of the appropriate type
        matching_providers = []
        for p in general_providers:
            if hasattr(p, 'provider_type') and isinstance(p.provider_type, str):
                if p.provider_type == claim_type or claim_type in p.provider_type:
                    matching_providers.append(p)
        if not matching_providers:
            matching_providers = general_providers  # Fallback if no matching provider
        provider = random.choice(matching_providers)
        
        # Select a service
        if claim_type in GENERAL_TREATMENT_SERVICES:
            service = random.choice(GENERAL_TREATMENT_SERVICES[claim_type])
            service_description = service['description']
            charged_amount = service['fee']
        else:
            service_description = f"{claim_type} service"
            charged_amount = round(random.uniform(50, 300), 2)
        
        # Generate service date (within the last 90 days from simulation date)
        service_date_date = simulation_date - timedelta(days=random.randint(1, 90))
        service_date = generate_random_datetime(service_date_date)
        
        # Generate submission date (a few days after service date, but not after simulation date)
        days_after_service = random.randint(1, 10)
        submission_date_date = min(service_date_date + timedelta(days=days_after_service), simulation_date)
        submission_date = generate_random_datetime(submission_date_date)
        
        # Calculate insurance amount (typically a percentage of charged amount for extras)
        benefit_percentage = random.uniform(0.5, 0.8)  # 50-80% benefit
        insurance_amount = round(charged_amount * benefit_percentage, 2)
        
        # No Medicare for general treatment
        medicare_amount = 0.0
        
        # No excess for general treatment
        excess_applied = 0.0
        
        # Calculate gap amount
        gap_amount = round(charged_amount - insurance_amount, 2)
        
        # Generate claim number
        claim_number = generate_claim_number(simulation_date)
        
        # Determine claim status
        status = random.choices(
            ['Submitted', 'In Process', 'Approved', 'Paid', 'Rejected'],
            weights=[0.1, 0.1, 0.2, 0.5, 0.1],
            k=1
        )[0]
        
        # Generate processed date and payment date if applicable
        processed_date = None
        payment_date = None
        rejection_reason = None
        
        if status in ['Approved', 'Paid']:
            # Processed date should be between submission date and simulation date
            max_days_after_submission = max(0, (simulation_date - submission_date_date).days)
            if max_days_after_submission > 0:
                days_after_submission = random.randint(1, min(7, max_days_after_submission))
                processed_date_date = submission_date_date + timedelta(days=days_after_submission)
                processed_date = generate_random_datetime(processed_date_date)
                
                if status == 'Paid' and processed_date_date < simulation_date:
                    # Payment date should be between processed date and simulation date
                    max_days_after_processed = max(0, (simulation_date - processed_date_date).days)
                    if max_days_after_processed > 0:
                        days_after_processed = random.randint(1, min(3, max_days_after_processed))
                        payment_date_date = processed_date_date + timedelta(days=days_after_processed)
                        payment_date = generate_random_datetime(payment_date_date)
        elif status == 'Rejected':
            # Processed date should be between submission date and simulation date
            max_days_after_submission = max(0, (simulation_date - submission_date_date).days)
            if max_days_after_submission > 0:
                days_after_submission = random.randint(1, min(7, max_days_after_submission))
                processed_date_date = submission_date_date + timedelta(days=days_after_submission)
                processed_date = generate_random_datetime(processed_date_date)
            
            rejection_reasons = [
                'Service not covered by policy',
                'Annual limit reached',
                'Waiting period not served',
                'Insufficient documentation',
                'Duplicate claim'
            ]
            rejection_reason = random.choice(rejection_reasons)
        
        # Create the claim
        claim = Claim(
            claim_number=claim_number,
            policy_id=policies.index(policy) + 1,  # Assuming PolicyID starts at 1
            member_id=member_id,
            provider_id=providers.index(provider) + 1,  # Assuming ProviderID starts at 1
            service_date=service_date,
            submission_date=submission_date,
            claim_type=claim_type,
            service_description=service_description,
            charged_amount=charged_amount,
            medicare_amount=medicare_amount,
            insurance_amount=insurance_amount,
            gap_amount=gap_amount,
            excess_applied=excess_applied,
            status=status,
            processed_date=processed_date,
            payment_date=payment_date,
            rejection_reason=rejection_reason
        )
        
        claims.append(claim)
    
    logger.info(f"Generated {len(claims)} general treatment claims")
    return claims


class ClaimsSimulation:
    """
    Class for simulating health insurance claims.
    """
    
    def __init__(self):
        """Initialize the claims simulation."""
        self.policies = []
        self.members = []
        self.providers = []
        self.load_data()
    
    def load_data(self):
        """Load data from the database."""
        # Load policies
        policy_data = execute_query("SELECT * FROM Insurance.Policies WHERE Status = 'Active'")
        self.policies = [Policy(**p) for p in policy_data]
        
        # Load members
        member_data = execute_query("SELECT * FROM Insurance.Members WHERE IsActive = 1")
        self.members = [Member(**m) for m in member_data]
        
        # Load providers
        provider_data = execute_query("SELECT * FROM Insurance.Providers WHERE IsActive = 1")
        self.providers = [Provider(**p) for p in provider_data]
    
    def generate_hospital_claims(self, count: int, simulation_date: date) -> List[Claim]:
        """
        Generate hospital claims and insert them into the database.
        
        Args:
            count: Number of claims to generate
            simulation_date: The date to use for claim generation
            
        Returns:
            A list of generated claims
        """
        claims = generate_hospital_claims(
            self.policies, 
            self.members, 
            self.providers, 
            count, 
            simulation_date
        )
        
        # Insert claims into the database
        for claim in claims:
            query = """
            INSERT INTO Insurance.Claims (
                ClaimNumber, PolicyID, MemberID, ProviderID, ServiceDate, SubmissionDate,
                ClaimType, ServiceDescription, MBSItemNumber, ChargedAmount, MedicareAmount,
                InsuranceAmount, GapAmount, ExcessApplied, Status, ProcessedDate,
                PaymentDate, RejectionReason, LastModified
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            execute_non_query(query, (
                claim.claim_number, claim.policy_id, claim.member_id, claim.provider_id,
                claim.service_date, claim.submission_date, claim.claim_type,
                claim.service_description, claim.mbs_item_number, claim.charged_amount,
                claim.medicare_amount, claim.insurance_amount, claim.gap_amount,
                claim.excess_applied, claim.status, claim.processed_date,
                claim.payment_date, claim.rejection_reason, simulation_date
            ), simulation_date)
        
        logger.info(f"Inserted {len(claims)} hospital claims into the database")
        return claims
    
    def generate_general_treatment_claims(self, count: int, simulation_date: date) -> List[Claim]:
        """
        Generate general treatment claims and insert them into the database.
        
        Args:
            count: Number of claims to generate
            simulation_date: The date to use for claim generation
            
        Returns:
            A list of generated claims
        """
        claims = generate_general_treatment_claims(
            self.policies, 
            self.members, 
            self.providers, 
            count, 
            simulation_date
        )
        
        # Insert claims into the database
        for claim in claims:
            query = """
            INSERT INTO Insurance.Claims (
                ClaimNumber, PolicyID, MemberID, ProviderID, ServiceDate, SubmissionDate,
                ClaimType, ServiceDescription, MBSItemNumber, ChargedAmount, MedicareAmount,
                InsuranceAmount, GapAmount, ExcessApplied, Status, ProcessedDate,
                PaymentDate, RejectionReason, LastModified
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            execute_non_query(query, (
                claim.claim_number, claim.policy_id, claim.member_id, claim.provider_id,
                claim.service_date, claim.submission_date, claim.claim_type,
                claim.service_description, claim.mbs_item_number, claim.charged_amount,
                claim.medicare_amount, claim.insurance_amount, claim.gap_amount,
                claim.excess_applied, claim.status, claim.processed_date,
                claim.payment_date, claim.rejection_reason, simulation_date
            ), simulation_date)
        
        logger.info(f"Inserted {len(claims)} general treatment claims into the database")
        return claims