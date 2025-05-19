"""
Unit tests for the payments module.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta

from health_insurance_au.simulation.payments import (
    generate_premium_payments, generate_payment_reference
)
from health_insurance_au.models.models import Policy, PremiumPayment

class TestPaymentsModule:
    """Tests for the payments module."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_date = date(2022, 4, 15)
        
        # Create test policies
        self.test_policies = [
            # Policy with payment due on test date
            Policy(
                policy_number='POL10001',
                primary_member_id=1,
                plan_id=1,
                coverage_type='Single',
                start_date=date(2022, 1, 1),
                current_premium=200.0,
                premium_frequency='Monthly',
                last_premium_paid_date=date(2022, 3, 15),
                next_premium_due_date=self.test_date
            ),
            # Policy with payment due in the future
            Policy(
                policy_number='POL10002',
                primary_member_id=2,
                plan_id=2,
                coverage_type='Family',
                start_date=date(2022, 2, 1),
                current_premium=150.0,
                premium_frequency='Monthly',
                last_premium_paid_date=date(2022, 3, 20),
                next_premium_due_date=date(2022, 4, 20)
            ),
            # Policy with quarterly frequency
            Policy(
                policy_number='POL10003',
                primary_member_id=3,
                plan_id=3,
                coverage_type='Couple',
                start_date=date(2022, 1, 15),
                current_premium=450.0,
                premium_frequency='Quarterly',
                last_premium_paid_date=date(2022, 1, 15),
                next_premium_due_date=self.test_date
            )
        ]
        # Add policy_id attribute to simulate database ID
        setattr(self.test_policies[0], 'policy_id', 1)
        setattr(self.test_policies[1], 'policy_id', 2)
        setattr(self.test_policies[2], 'policy_id', 3)
    
    def test_generate_payment_reference(self):
        """Test generating a payment reference."""
        # Act
        payment_ref = generate_payment_reference(self.test_date)
        
        # Assert
        assert payment_ref.startswith('PMT-')
        assert self.test_date.strftime('%Y%m%d') in payment_ref
        assert len(payment_ref) == 19  # Format: PMT-YYYYMMDD-NNNNN
    
    def test_generate_payment_reference_default_date(self):
        """Test generating a payment reference with default date."""
        # Act
        payment_ref = generate_payment_reference()
        
        # Assert
        assert payment_ref.startswith('PMT-')
        assert date.today().strftime('%Y%m%d') in payment_ref
        assert len(payment_ref) == 19  # Format: PMT-YYYYMMDD-NNNNN
    
    @patch('health_insurance_au.simulation.payments.generate_payment_reference')
    def test_generate_premium_payments(self, mock_gen_reference):
        """Test generating premium payments."""
        # Arrange
        mock_gen_reference.side_effect = [
            'PMT-20220415-00001',
            'PMT-20220415-00002'
        ]
        
        # Act
        payments = generate_premium_payments(self.test_policies, self.test_date)
        
        # Assert
        assert len(payments) == 2  # Only policies with due date on test_date
        
        # Check first payment (monthly)
        assert payments[0].policy_id == 1
        assert payments[0].payment_date == self.test_date
        assert payments[0].payment_amount == 200.0
        assert payments[0].payment_method == 'Direct Debit'
        assert payments[0].payment_reference == 'PMT-20220415-00001'
        assert payments[0].period_start_date == self.test_date
        assert payments[0].period_end_date == self.test_date + timedelta(days=30)  # Next month
        
        # Check second payment (quarterly)
        assert payments[1].policy_id == 3
        assert payments[1].payment_date == self.test_date
        assert payments[1].payment_amount == 450.0
        assert payments[1].payment_method == 'Direct Debit'
        assert payments[1].payment_reference == 'PMT-20220415-00002'
        assert payments[1].period_start_date == self.test_date
        assert payments[1].period_end_date == self.test_date + timedelta(days=90)  # Next quarter
        
        # Check that policy dates were updated
        assert self.test_policies[0].last_premium_paid_date == self.test_date
        assert self.test_policies[0].next_premium_due_date == self.test_date + timedelta(days=30)
        
        assert self.test_policies[2].last_premium_paid_date == self.test_date
        assert self.test_policies[2].next_premium_due_date == self.test_date + timedelta(days=90)
    
    def test_generate_premium_payments_no_due_payments(self):
        """Test generating premium payments when none are due."""
        # Arrange
        policies = [
            # Policy with payment due in the future
            Policy(
                policy_number='POL10002',
                primary_member_id=2,
                plan_id=2,
                coverage_type='Family',
                start_date=date(2022, 2, 1),
                current_premium=150.0,
                premium_frequency='Monthly',
                last_premium_paid_date=date(2022, 3, 20),
                next_premium_due_date=date(2022, 4, 20)
            )
        ]
        setattr(policies[0], 'policy_id', 2)
        
        # Act
        payments = generate_premium_payments(policies, self.test_date)
        
        # Assert
        assert payments == []
    
    def test_generate_premium_payments_no_policies(self):
        """Test generating premium payments with no policies."""
        # Act
        payments = generate_premium_payments([], self.test_date)
        
        # Assert
        assert payments == []
    
    def test_generate_premium_payments_missing_dates(self):
        """Test generating premium payments for policies with missing payment dates."""
        # Arrange
        policies = [
            # Policy with missing next_premium_due_date
            Policy(
                policy_number='POL10004',
                primary_member_id=4,
                plan_id=4,
                coverage_type='Single',
                start_date=date(2022, 1, 1),
                current_premium=200.0,
                premium_frequency='Monthly',
                last_premium_paid_date=date(2022, 3, 15),
                next_premium_due_date=None
            )
        ]
        setattr(policies[0], 'policy_id', 4)
        
        # Act
        payments = generate_premium_payments(policies, self.test_date)
        
        # Assert
        assert payments == []
    
    def test_generate_premium_payments_different_payment_methods(self):
        """Test generating premium payments with different payment methods."""
        # Arrange
        policies = [
            # Policy with Credit Card payment method
            Policy(
                policy_number='POL10005',
                primary_member_id=5,
                plan_id=5,
                coverage_type='Single',
                start_date=date(2022, 1, 1),
                current_premium=200.0,
                premium_frequency='Monthly',
                payment_method='Credit Card',
                last_premium_paid_date=date(2022, 3, 15),
                next_premium_due_date=self.test_date
            )
        ]
        setattr(policies[0], 'policy_id', 5)
        
        # Act
        with patch('health_insurance_au.simulation.payments.generate_payment_reference') as mock_gen_ref:
            mock_gen_ref.return_value = 'PMT-20220415-00001'
            payments = generate_premium_payments(policies, self.test_date)
        
        # Assert
        assert len(payments) == 1
        assert payments[0].payment_method == 'Credit Card'
    
    def test_generate_premium_payments_annual_frequency(self):
        """Test generating premium payments with annual frequency."""
        # Arrange
        policies = [
            # Policy with annual payment frequency
            Policy(
                policy_number='POL10006',
                primary_member_id=6,
                plan_id=6,
                coverage_type='Single',
                start_date=date(2021, 4, 15),
                current_premium=2000.0,
                premium_frequency='Annually',
                last_premium_paid_date=date(2021, 4, 15),
                next_premium_due_date=self.test_date
            )
        ]
        setattr(policies[0], 'policy_id', 6)
        
        # Act
        with patch('health_insurance_au.simulation.payments.generate_payment_reference') as mock_gen_ref:
            mock_gen_ref.return_value = 'PMT-20220415-00001'
            payments = generate_premium_payments(policies, self.test_date)
        
        # Assert
        assert len(payments) == 1
        assert payments[0].period_start_date == self.test_date
        assert payments[0].period_end_date == self.test_date + timedelta(days=365)
        assert policies[0].next_premium_due_date == self.test_date + timedelta(days=365)