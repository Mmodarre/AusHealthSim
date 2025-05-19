"""
Financial transaction generation module for the Health Insurance AU simulation.
"""
import random
import string
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from health_insurance_au.models.models import FinancialTransaction, Policy, Claim
from health_insurance_au.utils.db_utils import bulk_insert
from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

class FinancialTransactionGenerator:
    """
    Class for generating financial transactions.
    """
    
    def __init__(self):
        """Initialize the financial transaction generator."""
        self.transaction_types = {
            'Premium': {
                'description_templates': [
                    "Premium payment for policy {policy_number}",
                    "Monthly premium for policy {policy_number}",
                    "Quarterly premium for policy {policy_number}",
                    "Annual premium for policy {policy_number}"
                ],
                'amount_range': (100.0, 800.0),
                'entity_type': 'Policy'
            },
            'ClaimPayment': {
                'description_templates': [
                    "Claim payment for claim {claim_number}",
                    "Benefit payment for claim {claim_number}",
                    "Provider payment for claim {claim_number}"
                ],
                'amount_range': (50.0, 3000.0),
                'entity_type': 'Claim'
            },
            'Refund': {
                'description_templates': [
                    "Premium refund for policy {policy_number}",
                    "Overpayment refund for policy {policy_number}",
                    "Cancellation refund for policy {policy_number}"
                ],
                'amount_range': (20.0, 500.0),
                'entity_type': 'Policy'
            },
            'Adjustment': {
                'description_templates': [
                    "Premium adjustment for policy {policy_number}",
                    "Rate adjustment for policy {policy_number}",
                    "Coverage change adjustment for policy {policy_number}"
                ],
                'amount_range': (10.0, 200.0),
                'entity_type': 'Policy'
            },
            'Fee': {
                'description_templates': [
                    "Administrative fee for policy {policy_number}",
                    "Late payment fee for policy {policy_number}",
                    "Processing fee for policy {policy_number}"
                ],
                'amount_range': (5.0, 50.0),
                'entity_type': 'Policy'
            }
        }
    
    def _generate_reference_number(self, transaction_type: str, simulation_date: date) -> str:
        """
        Generate a reference number for a transaction.
        
        Args:
            transaction_type: The type of transaction
            simulation_date: The simulation date
            
        Returns:
            A reference number string
        """
        date_str = simulation_date.strftime('%Y%m%d')
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        if transaction_type == 'Premium':
            prefix = 'PMT'
        elif transaction_type == 'ClaimPayment':
            prefix = 'CLM'
        elif transaction_type == 'Refund':
            prefix = 'RFD'
        elif transaction_type == 'Adjustment':
            prefix = 'ADJ'
        elif transaction_type == 'Fee':
            prefix = 'FEE'
        else:
            prefix = 'TXN'
            
        return f"{prefix}-{date_str}-{random_chars}"
    
    def generate_premium_transactions(self, policies: List[Policy], simulation_date: date = None) -> List[FinancialTransaction]:
        """
        Generate premium payment transactions.
        
        Args:
            policies: List of policies to generate transactions for
            simulation_date: The simulation date
            
        Returns:
            A list of FinancialTransaction objects
        """
        if simulation_date is None:
            simulation_date = date.today()
        
        transactions = []
        
        # Select a subset of policies for transactions
        transaction_count = max(1, int(len(policies) * 0.2))  # 20% of policies
        selected_policies = random.sample(policies, min(transaction_count, len(policies)))
        
        for policy in selected_policies:
            transaction_type = 'Premium'
            policy_number = policy.policy_number
            policy_id = getattr(policy, 'policy_id', 0)
            
            # Generate transaction details
            description_template = random.choice(self.transaction_types[transaction_type]['description_templates'])
            description = description_template.format(policy_number=policy_number)
            
            amount = policy.current_premium
            reference_number = self._generate_reference_number(transaction_type, simulation_date)
            
            # Create the transaction
            transaction = FinancialTransaction(
                transaction_type=transaction_type,
                transaction_date=simulation_date,
                amount=amount,
                description=description,
                reference_number=reference_number,
                related_entity_type=self.transaction_types[transaction_type]['entity_type'],
                related_entity_id=policy_id,
                processed_date=datetime.combine(simulation_date, datetime.min.time()),
                status='Completed',
                created_by='System',
                created_date=datetime.combine(simulation_date, datetime.min.time()),
                last_modified=datetime.combine(simulation_date, datetime.min.time())
            )
            
            transactions.append(transaction)
        
        logger.info(f"Generated {len(transactions)} premium transactions")
        return transactions
    
    def generate_claim_payment_transactions(self, claims: List[Claim], simulation_date: date = None) -> List[FinancialTransaction]:
        """
        Generate claim payment transactions.
        
        Args:
            claims: List of claims to generate transactions for
            simulation_date: The simulation date
            
        Returns:
            A list of FinancialTransaction objects
        """
        if simulation_date is None:
            simulation_date = date.today()
        
        transactions = []
        
        # Filter claims that are in 'Approved' or 'Paid' status
        eligible_claims = [claim for claim in claims if claim.status in ['Approved', 'Paid']]
        
        for claim in eligible_claims:
            transaction_type = 'ClaimPayment'
            claim_number = claim.claim_number
            claim_id = getattr(claim, 'claim_id', 0)
            
            # Generate transaction details
            description_template = random.choice(self.transaction_types[transaction_type]['description_templates'])
            description = description_template.format(claim_number=claim_number)
            
            amount = claim.insurance_amount
            reference_number = self._generate_reference_number(transaction_type, simulation_date)
            
            # Create the transaction
            transaction = FinancialTransaction(
                transaction_type=transaction_type,
                transaction_date=simulation_date,
                amount=amount,
                description=description,
                reference_number=reference_number,
                related_entity_type=self.transaction_types[transaction_type]['entity_type'],
                related_entity_id=claim_id,
                processed_date=datetime.combine(simulation_date, datetime.min.time()),
                status='Completed',
                created_by='System',
                created_date=datetime.combine(simulation_date, datetime.min.time()),
                last_modified=datetime.combine(simulation_date, datetime.min.time())
            )
            
            transactions.append(transaction)
        
        logger.info(f"Generated {len(transactions)} claim payment transactions")
        return transactions
    
    def generate_miscellaneous_transactions(self, policies: List[Policy], simulation_date: date = None, count: int = 10) -> List[FinancialTransaction]:
        """
        Generate miscellaneous transactions (refunds, adjustments, fees).
        
        Args:
            policies: List of policies to generate transactions for
            simulation_date: The simulation date
            count: Number of transactions to generate
            
        Returns:
            A list of FinancialTransaction objects
        """
        if simulation_date is None:
            simulation_date = date.today()
        
        transactions = []
        
        # Select random policies for transactions
        selected_policies = random.sample(policies, min(count, len(policies)))
        
        for policy in selected_policies:
            # Select a random transaction type
            transaction_type = random.choice(['Refund', 'Adjustment', 'Fee'])
            policy_number = policy.policy_number
            policy_id = getattr(policy, 'policy_id', 0)
            
            # Generate transaction details
            description_template = random.choice(self.transaction_types[transaction_type]['description_templates'])
            description = description_template.format(policy_number=policy_number)
            
            min_amount, max_amount = self.transaction_types[transaction_type]['amount_range']
            amount = round(random.uniform(min_amount, max_amount), 2)
            reference_number = self._generate_reference_number(transaction_type, simulation_date)
            
            # Create the transaction
            transaction = FinancialTransaction(
                transaction_type=transaction_type,
                transaction_date=simulation_date,
                amount=amount,
                description=description,
                reference_number=reference_number,
                related_entity_type=self.transaction_types[transaction_type]['entity_type'],
                related_entity_id=policy_id,
                processed_date=datetime.combine(simulation_date, datetime.min.time()),
                status='Completed',
                created_by='System',
                created_date=datetime.combine(simulation_date, datetime.min.time()),
                last_modified=datetime.combine(simulation_date, datetime.min.time())
            )
            
            transactions.append(transaction)
        
        logger.info(f"Generated {len(transactions)} miscellaneous transactions")
        return transactions
    
    def save_transactions(self, transactions: List[FinancialTransaction], simulation_date: date = None) -> int:
        """
        Save transactions to the database.
        
        Args:
            transactions: List of transactions to save
            simulation_date: The simulation date
            
        Returns:
            Number of transactions saved
        """
        if not transactions:
            return 0
            
        if simulation_date is None:
            simulation_date = date.today()
        
        transaction_dicts = [transaction.to_dict() for transaction in transactions]
        
        try:
            rows_affected = bulk_insert("Insurance.FinancialTransactions", transaction_dicts, simulation_date)
            logger.info(f"Saved {rows_affected} transactions to database")
            return rows_affected
        except Exception as e:
            logger.error(f"Error saving transactions: {e}")
            return 0