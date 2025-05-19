"""
Financial transaction generator for enhanced simulation.
"""
from datetime import date, datetime, timedelta
import random
import string
from typing import Dict, List, Any, Optional

from health_insurance_au.utils.db_utils import execute_query, execute_non_query, bulk_insert
from health_insurance_au.models.models import FinancialTransaction

class FinancialTransactionGenerator:
    """Generator for financial transactions."""
    
    def __init__(self):
        """Initialize the financial transaction generator."""
        pass
    
    def generate_transactions(self, simulation_date: date, detail_level: int = 2) -> Dict[str, int]:
        """
        Generate financial transactions.
        
        Args:
            simulation_date: The simulation date
            detail_level: The level of detail for transactions (1-3)
            
        Returns:
            Dictionary with statistics about generated transactions
        """
        transactions = []
        
        # Generate premium payment transactions
        premium_transactions = self._generate_premium_transactions(simulation_date)
        transactions.extend(premium_transactions)
        
        # Generate claim payment transactions
        claim_transactions = self._generate_claim_transactions(simulation_date)
        transactions.extend(claim_transactions)
        
        # If detail level is higher, generate more transaction types
        if detail_level >= 2:
            # Generate refund transactions
            refund_transactions = self._generate_refund_transactions(simulation_date)
            transactions.extend(refund_transactions)
            
            # Generate adjustment transactions
            adjustment_transactions = self._generate_adjustment_transactions(simulation_date)
            transactions.extend(adjustment_transactions)
        
        # If detail level is highest, generate even more transaction types
        if detail_level >= 3:
            # Generate fee transactions
            fee_transactions = self._generate_fee_transactions(simulation_date)
            transactions.extend(fee_transactions)
            
            # Generate interest transactions
            interest_transactions = self._generate_interest_transactions(simulation_date)
            transactions.extend(interest_transactions)
        
        # Insert transactions into the database
        if transactions:
            transaction_dicts = [t.to_dict() for t in transactions]
            rows_affected = bulk_insert("Insurance.FinancialTransactions", transaction_dicts)
        else:
            rows_affected = 0
        
        return {
            'transactions_generated': rows_affected
        }
    
    def _generate_premium_transactions(self, simulation_date: date) -> List[FinancialTransaction]:
        """Generate premium payment transactions."""
        transactions = []
        
        # Get policies with premium due dates on or before the simulation date
        try:
            query = """
            SELECT p.PolicyID, p.PolicyNumber, p.CurrentPremium, p.PaymentMethod
            FROM Insurance.Policies p
            WHERE p.Status = 'Active'
            AND p.NextPremiumDueDate <= ?
            """
            policies = execute_query(query, (simulation_date,))
            
            for policy in policies:
                # Generate a transaction reference
                reference = self._generate_payment_reference(simulation_date)
                
                # Create a transaction
                transaction = FinancialTransaction(
                    transaction_type="Premium Payment",
                    transaction_date=simulation_date,
                    amount=policy['CurrentPremium'],
                    description=f"Premium payment for policy {policy['PolicyNumber']}",
                    reference_number=reference,
                    related_entity_type="Policy",
                    related_entity_id=policy['PolicyID'],
                    processed_date=datetime.combine(simulation_date, datetime.min.time()),
                    status="Successful",
                    created_by="System"
                )
                
                transactions.append(transaction)
        except Exception as e:
            print(f"Error generating premium transactions: {e}")
        
        return transactions
    
    def _generate_claim_transactions(self, simulation_date: date) -> List[FinancialTransaction]:
        """Generate claim payment transactions."""
        transactions = []
        
        # Get approved claims that haven't been paid yet
        try:
            query = """
            SELECT c.ClaimID, c.ClaimNumber, c.InsuranceAmount, p.PolicyNumber
            FROM Insurance.Claims c
            JOIN Insurance.Policies p ON c.PolicyID = p.PolicyID
            WHERE c.Status = 'Approved'
            AND c.PaymentDate IS NULL
            """
            claims = execute_query(query)
            
            for claim in claims:
                # Generate a transaction reference
                reference = self._generate_payment_reference(simulation_date)
                
                # Create a transaction
                transaction = FinancialTransaction(
                    transaction_type="Claim Payment",
                    transaction_date=simulation_date,
                    amount=claim['InsuranceAmount'],
                    description=f"Claim payment for claim {claim['ClaimNumber']}",
                    reference_number=reference,
                    related_entity_type="Claim",
                    related_entity_id=claim['ClaimID'],
                    processed_date=datetime.combine(simulation_date, datetime.min.time()),
                    status="Successful",
                    created_by="System"
                )
                
                transactions.append(transaction)
                
                # Update the claim with payment date
                try:
                    update_query = """
                    UPDATE Insurance.Claims
                    SET PaymentDate = ?, Status = 'Paid', LastModified = ?
                    WHERE ClaimID = ?
                    """
                    execute_non_query(update_query, (simulation_date, simulation_date, claim['ClaimID']))
                except Exception as e:
                    print(f"Error updating claim {claim['ClaimID']}: {e}")
        except Exception as e:
            print(f"Error generating claim transactions: {e}")
        
        return transactions
    
    def _generate_refund_transactions(self, simulation_date: date) -> List[FinancialTransaction]:
        """Generate refund transactions."""
        transactions = []
        
        # Get a small random subset of policies for refunds
        try:
            query = """
            SELECT TOP 5 p.PolicyID, p.PolicyNumber, p.CurrentPremium
            FROM Insurance.Policies p
            WHERE p.Status = 'Active'
            ORDER BY NEWID()
            """
            policies = execute_query(query)
            
            for policy in policies:
                # Only generate refunds for a small percentage of policies
                if random.random() > 0.2:
                    continue
                
                # Generate a refund amount (partial premium)
                refund_amount = round(policy['CurrentPremium'] * random.uniform(0.1, 0.5), 2)
                
                # Generate a transaction reference
                reference = self._generate_payment_reference(simulation_date)
                
                # Create a transaction
                transaction = FinancialTransaction(
                    transaction_type="Refund",
                    transaction_date=simulation_date,
                    amount=refund_amount,
                    description=f"Premium refund for policy {policy['PolicyNumber']}",
                    reference_number=reference,
                    related_entity_type="Policy",
                    related_entity_id=policy['PolicyID'],
                    processed_date=datetime.combine(simulation_date, datetime.min.time()),
                    status="Successful",
                    created_by="System"
                )
                
                transactions.append(transaction)
        except Exception as e:
            print(f"Error generating refund transactions: {e}")
        
        return transactions
    
    def _generate_adjustment_transactions(self, simulation_date: date) -> List[FinancialTransaction]:
        """Generate adjustment transactions."""
        transactions = []
        
        # Get a small random subset of policies for adjustments
        try:
            query = """
            SELECT TOP 5 p.PolicyID, p.PolicyNumber, p.CurrentPremium
            FROM Insurance.Policies p
            WHERE p.Status = 'Active'
            ORDER BY NEWID()
            """
            policies = execute_query(query)
            
            for policy in policies:
                # Only generate adjustments for a small percentage of policies
                if random.random() > 0.2:
                    continue
                
                # Generate an adjustment amount (small percentage of premium)
                adjustment_amount = round(policy['CurrentPremium'] * random.uniform(0.05, 0.15), 2)
                
                # Randomly decide if it's a positive or negative adjustment
                if random.random() > 0.5:
                    adjustment_amount = -adjustment_amount
                
                # Generate a transaction reference
                reference = self._generate_payment_reference(simulation_date)
                
                # Create a transaction
                transaction = FinancialTransaction(
                    transaction_type="Adjustment",
                    transaction_date=simulation_date,
                    amount=adjustment_amount,
                    description=f"Premium adjustment for policy {policy['PolicyNumber']}",
                    reference_number=reference,
                    related_entity_type="Policy",
                    related_entity_id=policy['PolicyID'],
                    processed_date=datetime.combine(simulation_date, datetime.min.time()),
                    status="Successful",
                    created_by="System"
                )
                
                transactions.append(transaction)
        except Exception as e:
            print(f"Error generating adjustment transactions: {e}")
        
        return transactions
    
    def _generate_fee_transactions(self, simulation_date: date) -> List[FinancialTransaction]:
        """Generate fee transactions."""
        transactions = []
        
        # Get a small random subset of policies for fees
        try:
            query = """
            SELECT TOP 5 p.PolicyID, p.PolicyNumber
            FROM Insurance.Policies p
            WHERE p.Status = 'Active'
            ORDER BY NEWID()
            """
            policies = execute_query(query)
            
            for policy in policies:
                # Only generate fees for a small percentage of policies
                if random.random() > 0.1:
                    continue
                
                # Generate a fee amount
                fee_amount = random.choice([15.0, 25.0, 30.0, 50.0])
                
                # Generate a transaction reference
                reference = self._generate_payment_reference(simulation_date)
                
                # Create a transaction
                transaction = FinancialTransaction(
                    transaction_type="Administrative Fee",
                    transaction_date=simulation_date,
                    amount=fee_amount,
                    description=f"Administrative fee for policy {policy['PolicyNumber']}",
                    reference_number=reference,
                    related_entity_type="Policy",
                    related_entity_id=policy['PolicyID'],
                    processed_date=datetime.combine(simulation_date, datetime.min.time()),
                    status="Successful",
                    created_by="System"
                )
                
                transactions.append(transaction)
        except Exception as e:
            print(f"Error generating fee transactions: {e}")
        
        return transactions
    
    def _generate_interest_transactions(self, simulation_date: date) -> List[FinancialTransaction]:
        """Generate interest transactions."""
        transactions = []
        
        # Only generate interest transactions on the first day of the month
        if simulation_date.day != 1:
            return transactions
        
        # Get a small random subset of policies for interest
        try:
            query = """
            SELECT TOP 10 p.PolicyID, p.PolicyNumber, p.CurrentPremium
            FROM Insurance.Policies p
            WHERE p.Status = 'Active'
            ORDER BY NEWID()
            """
            policies = execute_query(query)
            
            for policy in policies:
                # Only generate interest for a small percentage of policies
                if random.random() > 0.3:
                    continue
                
                # Generate an interest amount (small percentage of premium)
                interest_amount = round(policy['CurrentPremium'] * random.uniform(0.01, 0.03), 2)
                
                # Generate a transaction reference
                reference = self._generate_payment_reference(simulation_date)
                
                # Create a transaction
                transaction = FinancialTransaction(
                    transaction_type="Interest",
                    transaction_date=simulation_date,
                    amount=interest_amount,
                    description=f"Interest for policy {policy['PolicyNumber']}",
                    reference_number=reference,
                    related_entity_type="Policy",
                    related_entity_id=policy['PolicyID'],
                    processed_date=datetime.combine(simulation_date, datetime.min.time()),
                    status="Successful",
                    created_by="System"
                )
                
                transactions.append(transaction)
        except Exception as e:
            print(f"Error generating interest transactions: {e}")
        
        return transactions
    
    def _generate_payment_reference(self, payment_date: date) -> str:
        """
        Generate a random payment reference.
        
        Args:
            payment_date: The date to use in the reference
            
        Returns:
            A payment reference string in the format PMT-YYYYMMDD-NNNNN
        """
        # Format: PMT-YYYYMMDD-NNNNN where YYYYMMDD is the payment date and NNNNN is a 5-digit number
        date_str = payment_date.strftime('%Y%m%d')
        number = ''.join(random.choices(string.digits, k=5))
        return f"PMT-{date_str}-{number}"