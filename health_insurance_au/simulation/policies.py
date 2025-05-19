"""
Policy generator for the Health Insurance AU simulation.
"""
import random
import string
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from health_insurance_au.models.models import Policy, PolicyMember, Member, CoveragePlan
from health_insurance_au.utils.logging_config import get_logger
from health_insurance_au.utils.db_utils import execute_query

# Set up logging
logger = get_logger(__name__)

def generate_policy_number() -> str:
    """Generate a random policy number."""
    # Format: POL-XX-NNNNNN where XX is a state code and NNNNNN is a 6-digit number
    state_codes = ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT']
    state_code = random.choice(state_codes)
    number = ''.join(random.choices(string.digits, k=6))
    return f"POL-{state_code}-{number}"

def calculate_premium(plan: CoveragePlan, coverage_type: str, excess_amount: float) -> float:
    """
    Calculate the premium for a policy based on coverage plan, type, and excess.
    
    Args:
        plan: The coverage plan
        coverage_type: The coverage type (Single, Couple, Family, Single Parent)
        excess_amount: The excess amount
        
    Returns:
        The calculated premium amount
    """
    base_premium = plan.monthly_premium
    
    # Apply multiplier based on coverage type
    if coverage_type == 'Single':
        multiplier = 1.0
    elif coverage_type == 'Couple':
        multiplier = 2.0
    elif coverage_type == 'Family':
        multiplier = 2.5
    elif coverage_type == 'Single Parent':
        multiplier = 1.5
    else:
        multiplier = 1.0
    
    # Apply discount for higher excess (only for hospital and combined plans)
    excess_discount = 0.0
    if plan.plan_type in ['Hospital', 'Combined'] and excess_amount > 0:
        if excess_amount == 250:
            excess_discount = 0.05
        elif excess_amount == 500:
            excess_discount = 0.10
        elif excess_amount == 750:
            excess_discount = 0.15
    
    # Calculate final premium
    premium = base_premium * multiplier * (1 - excess_discount)
    
    # Round to 2 decimal places
    return round(premium, 2)

def generate_policies(members: List[Member], plans: List[CoveragePlan], count: int = 10, simulation_date: date = None) -> Tuple[List[Policy], List[PolicyMember]]:
    """
    Generate policies for members.
    
    Args:
        members: List of members to create policies for
        plans: List of available coverage plans
        count: Number of policies to generate
        simulation_date: The date to use for policy generation (default: today)
        
    Returns:
        A tuple of (policies, policy_members)
    """
    if not members or not plans:
        logger.warning("No members or plans available to generate policies")
        return [], []
    
    if simulation_date is None:
        simulation_date = date.today()
    
    # Ensure we don't try to create more policies than we have members
    count = min(count, len(members))
    
    policies = []
    policy_members = []
    
    # Track which members already have policies
    members_with_policies = set()
    
    # Get existing policy-member relationships from the database
    existing_relationships = execute_query("SELECT PolicyID, MemberID FROM Insurance.PolicyMembers")
    existing_policy_member_pairs = set((r['PolicyID'], r['MemberID']) for r in existing_relationships)
    
    # Get the next available PolicyID
    policy_id_result = execute_query("SELECT MAX(PolicyID) as MaxID FROM Insurance.Policies")
    next_policy_id = 1
    if policy_id_result and policy_id_result[0]['MaxID'] is not None:
        next_policy_id = policy_id_result[0]['MaxID'] + 1
    
    logger.info(f"Starting with PolicyID: {next_policy_id}")
    
    for i in range(count):
        # Find a member who doesn't already have a policy
        available_members = [m for idx, m in enumerate(members) if idx not in members_with_policies]
        if not available_members:
            logger.warning("All members already have policies")
            break
            
        primary_member = random.choice(available_members)
        primary_member_idx = members.index(primary_member)
        members_with_policies.add(primary_member_idx)
        
        # Select a plan
        plan = random.choice(plans)
        
        # Determine coverage type and add additional members if needed
        coverage_type = random.choices(
            ['Single', 'Couple', 'Family', 'Single Parent'],
            weights=[0.4, 0.3, 0.2, 0.1],
            k=1
        )[0]
        
        # Generate policy number
        policy_number = generate_policy_number()
        
        # Determine excess amount
        excess_amount = 0.0
        if plan.plan_type in ['Hospital', 'Combined'] and plan.excess_options:
            excess_amount = random.choice(plan.excess_options)
        
        # Calculate premium
        premium = calculate_premium(plan, coverage_type, excess_amount)
        
        # Apply rebate (simplified)
        rebate_percentage = 0.0
        if primary_member.phi_rebate_tier == 'Base':
            rebate_percentage = 24.608  # Base tier for under 65
        elif primary_member.phi_rebate_tier == 'Tier1':
            rebate_percentage = 16.405
        elif primary_member.phi_rebate_tier == 'Tier2':
            rebate_percentage = 8.202
        
        # Apply LHC loading
        lhc_loading_percentage = primary_member.lhc_loading_percentage
        
        # Generate start date (between 1 and 3 years ago, relative to simulation date)
        start_date = simulation_date - timedelta(days=random.randint(30, 1095))
        
        # Determine payment frequency
        payment_frequency = random.choices(
            ['Monthly', 'Quarterly', 'Annually'],
            weights=[0.7, 0.2, 0.1],
            k=1
        )[0]
        
        # Determine payment method
        payment_method = random.choices(
            ['Direct Debit', 'Credit Card', 'BPAY', 'PayPal'],
            weights=[0.6, 0.3, 0.08, 0.02],
            k=1
        )[0]
        
        # Generate last premium paid date and next due date (relative to simulation date)
        last_paid_date = simulation_date - timedelta(days=random.randint(0, 30))
        
        if payment_frequency == 'Monthly':
            next_due_date = last_paid_date + timedelta(days=30)
        elif payment_frequency == 'Quarterly':
            next_due_date = last_paid_date + timedelta(days=90)
        else:  # Annually
            next_due_date = last_paid_date + timedelta(days=365)
        
        # Create the policy
        policy = Policy(
            policy_number=policy_number,
            primary_member_id=primary_member_idx + 1,  # Assuming MemberID starts at 1
            plan_id=plans.index(plan) + 1,  # Assuming PlanID starts at 1
            coverage_type=coverage_type,
            start_date=start_date,
            current_premium=premium,
            premium_frequency=payment_frequency,
            excess_amount=excess_amount,
            rebate_percentage=rebate_percentage,
            lhc_loading_percentage=lhc_loading_percentage,
            payment_method=payment_method,
            last_premium_paid_date=last_paid_date,
            next_premium_due_date=next_due_date
        )
        
        policies.append(policy)
        
        current_policy_id = next_policy_id + i
        
        # Check if the primary member can be added to this policy
        primary_member_db_id = primary_member_idx + 1
        if (current_policy_id, primary_member_db_id) not in existing_policy_member_pairs:
            # Add primary member to policy_members
            policy_member = PolicyMember(
                policy_id=current_policy_id,
                member_id=primary_member_db_id,
                relationship_to_primary='Self',
                start_date=start_date
            )
            
            policy_members.append(policy_member)
            # Track this relationship to avoid duplicates in the current batch
            existing_policy_member_pairs.add((current_policy_id, primary_member_db_id))
        else:
            logger.warning(f"Skipping duplicate policy-member relationship: Policy {current_policy_id}, Member {primary_member_db_id}")
        
        # Add additional members based on coverage type
        if coverage_type in ['Couple', 'Family']:
            # Try to find a partner (similar age)
            partner_candidates = [
                idx for idx, m in enumerate(members) 
                if idx not in members_with_policies 
                and abs((m.date_of_birth.year - primary_member.date_of_birth.year)) < 15
            ]
            
            if partner_candidates:
                partner_idx = random.choice(partner_candidates)
                members_with_policies.add(partner_idx)
                
                partner_db_id = partner_idx + 1
                if (current_policy_id, partner_db_id) not in existing_policy_member_pairs:
                    policy_member = PolicyMember(
                        policy_id=current_policy_id,
                        member_id=partner_db_id,
                        relationship_to_primary='Spouse',
                        start_date=start_date
                    )
                    
                    policy_members.append(policy_member)
                    # Track this relationship
                    existing_policy_member_pairs.add((current_policy_id, partner_db_id))
                else:
                    logger.warning(f"Skipping duplicate policy-member relationship: Policy {current_policy_id}, Member {partner_db_id}")
        
        if coverage_type in ['Family', 'Single Parent']:
            # Try to find 1-3 children (much younger)
            child_count = random.randint(1, 3)
            child_candidates = [
                idx for idx, m in enumerate(members) 
                if idx not in members_with_policies 
                and (primary_member.date_of_birth.year - m.date_of_birth.year) > 18
            ]
            
            for _ in range(min(child_count, len(child_candidates))):
                if not child_candidates:
                    break
                    
                child_idx = random.choice(child_candidates)
                child_candidates.remove(child_idx)
                members_with_policies.add(child_idx)
                
                child_db_id = child_idx + 1
                if (current_policy_id, child_db_id) not in existing_policy_member_pairs:
                    policy_member = PolicyMember(
                        policy_id=current_policy_id,
                        member_id=child_db_id,
                        relationship_to_primary='Child',
                        start_date=start_date
                    )
                    
                    policy_members.append(policy_member)
                    # Track this relationship
                    existing_policy_member_pairs.add((current_policy_id, child_db_id))
                else:
                    logger.warning(f"Skipping duplicate policy-member relationship: Policy {current_policy_id}, Member {child_db_id}")
    
    logger.info(f"Generated {len(policies)} policies with {len(policy_members)} members")
    return policies, policy_members