"""
Premium payments generator for the Health Insurance AU simulation.
"""
import random
import string
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from health_insurance_au.models.models import PremiumPayment, Policy
from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

def generate_payment_reference() -> str:
    """Generate a random payment reference."""
    # Format: PMT-YYYYMMDD-NNNNN where YYYYMMDD is the current date and NNNNN is a 5-digit number
    today = date.today().strftime('%Y%m%d')
    number = ''.join(random.choices(string.digits, k=5))
    return f"PMT-{today}-{number}"

def generate_premium_payments(policies: List[Policy], simulation_date: date) -> List[PremiumPayment]:
    """
    Generate premium payments for policies due on the simulation date.
    
    Args:
        policies: List of policies
        simulation_date: The date to check for due payments
        
    Returns:
        A list of PremiumPayment objects
    """
    payments = []
    
    # Filter for active policies with payments due on or before the simulation date
    due_policies = [p for p in policies if p.status == 'Active' and p.next_premium_due_date and p.next_premium_due_date <= simulation_date]
    
    logger.info(f"Found {len(due_policies)} policies with payments due on or before {simulation_date}")
    
    for policy in due_policies:
        # Determine payment amount
        payment_amount = policy.current_premium
        
        # Determine payment method (use the one from the policy)
        payment_method = policy.payment_method
        
        # Generate payment reference
        payment_reference = generate_payment_reference()
        
        # Determine payment status (most are successful)
        payment_status = random.choices(
            ['Successful', 'Failed', 'Pending'],
            weights=[0.95, 0.03, 0.02],
            k=1
        )[0]
        
        # Determine period start and end dates
        period_start_date = policy.next_premium_due_date
        
        if policy.premium_frequency == 'Monthly':
            period_end_date = period_start_date + timedelta(days=30)
            next_due_date = period_end_date
        elif policy.premium_frequency == 'Quarterly':
            period_end_date = period_start_date + timedelta(days=90)
            next_due_date = period_end_date
        else:  # Annually
            period_end_date = period_start_date + timedelta(days=365)
            next_due_date = period_end_date
        
        # Create the payment
        payment = PremiumPayment(
            policy_id=policies.index(policy) + 1,  # Assuming PolicyID starts at 1
            payment_date=simulation_date,
            payment_amount=payment_amount,
            payment_method=payment_method,
            payment_reference=payment_reference,
            payment_status=payment_status,
            period_start_date=period_start_date,
            period_end_date=period_end_date
        )
        
        payments.append(payment)
        
        # Update the policy with new payment dates
        policy.last_premium_paid_date = simulation_date
        policy.next_premium_due_date = next_due_date
    
    logger.info(f"Generated {len(payments)} premium payments")
    return payments