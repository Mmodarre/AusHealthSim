"""
Unit tests for the data models.
"""
import pytest
import json
from datetime import date, datetime
from health_insurance_au.models.models import (
    Member, CoveragePlan, Policy, PolicyMember, Provider, Claim, PremiumPayment
)

class TestMember:
    """Tests for the Member class."""
    
    def test_member_creation(self):
        """Test creating a Member object."""
        # Arrange
        member_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': date(1980, 1, 1),
            'gender': 'Male',
            'address_line1': '123 Main St',
            'city': 'Sydney',
            'state': 'NSW',
            'post_code': '2000'
        }
        
        # Act
        member = Member(**member_data)
        
        # Assert
        assert member.first_name == 'John'
        assert member.last_name == 'Doe'
        assert member.date_of_birth == date(1980, 1, 1)
        assert member.gender == 'Male'
        assert member.address_line1 == '123 Main St'
        assert member.city == 'Sydney'
        assert member.state == 'NSW'
        assert member.post_code == '2000'
        assert member.country == 'Australia'  # Default value
        assert member.lhc_loading_percentage == 0.0  # Default value
        assert member.phi_rebate_tier == 'Base'  # Default value
        assert member.is_active == True  # Default value
    
    def test_member_to_dict(self):
        """Test converting a Member object to a dictionary."""
        # Arrange
        member = Member(
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1980, 1, 1),
            gender='Male',
            address_line1='123 Main St',
            city='Sydney',
            state='NSW',
            post_code='2000',
            member_number='M12345',
            title='Mr',
            email='john.doe@example.com',
            mobile_phone='0412345678',
            join_date=date(2020, 1, 1)
        )
        
        # Act
        result = member.to_dict()
        
        # Assert
        assert result['MemberNumber'] == 'M12345'
        assert result['Title'] == 'Mr'
        assert result['FirstName'] == 'John'
        assert result['LastName'] == 'Doe'
        assert result['DateOfBirth'] == date(1980, 1, 1)
        assert result['Gender'] == 'Male'
        assert result['Email'] == 'john.doe@example.com'
        assert result['MobilePhone'] == '0412345678'
        assert result['AddressLine1'] == '123 Main St'
        assert result['City'] == 'Sydney'
        assert result['State'] == 'NSW'
        assert result['PostCode'] == '2000'
        assert result['Country'] == 'Australia'
        assert result['JoinDate'] == date(2020, 1, 1)
        assert result['IsActive'] == True


class TestCoveragePlan:
    """Tests for the CoveragePlan class."""
    
    def test_coverage_plan_creation(self):
        """Test creating a CoveragePlan object."""
        # Arrange
        plan_data = {
            'plan_code': 'HOSP-GOLD',
            'plan_name': 'Gold Hospital Cover',
            'plan_type': 'Hospital',
            'monthly_premium': 200.0,
            'annual_premium': 2400.0,
            'effective_date': date(2022, 1, 1),
            'hospital_tier': 'Gold',
            'excess_options': [0, 250, 500],
            'waiting_periods': {'general': 2, 'pre-existing': 12},
            'coverage_details': {'private_room': True, 'ambulance': True}
        }
        
        # Act
        plan = CoveragePlan(**plan_data)
        
        # Assert
        assert plan.plan_code == 'HOSP-GOLD'
        assert plan.plan_name == 'Gold Hospital Cover'
        assert plan.plan_type == 'Hospital'
        assert plan.monthly_premium == 200.0
        assert plan.annual_premium == 2400.0
        assert plan.effective_date == date(2022, 1, 1)
        assert plan.hospital_tier == 'Gold'
        assert plan.excess_options == [0, 250, 500]
        assert plan.waiting_periods == {'general': 2, 'pre-existing': 12}
        assert plan.coverage_details == {'private_room': True, 'ambulance': True}
        assert plan.is_active == True  # Default value
        assert plan.end_date is None  # Default value
    
    def test_coverage_plan_to_dict(self):
        """Test converting a CoveragePlan object to a dictionary."""
        # Arrange
        plan = CoveragePlan(
            plan_code='HOSP-GOLD',
            plan_name='Gold Hospital Cover',
            plan_type='Hospital',
            monthly_premium=200.0,
            annual_premium=2400.0,
            effective_date=date(2022, 1, 1),
            hospital_tier='Gold',
            excess_options=[0, 250, 500],
            waiting_periods={'general': 2, 'pre-existing': 12},
            coverage_details={'private_room': True, 'ambulance': True}
        )
        
        # Act
        result = plan.to_dict()
        
        # Assert
        assert result['PlanCode'] == 'HOSP-GOLD'
        assert result['PlanName'] == 'Gold Hospital Cover'
        assert result['PlanType'] == 'Hospital'
        assert result['HospitalTier'] == 'Gold'
        assert result['MonthlyPremium'] == 200.0
        assert result['AnnualPremium'] == 2400.0
        assert result['ExcessOptions'] == json.dumps([0, 250, 500])
        assert result['WaitingPeriods'] == json.dumps({'general': 2, 'pre-existing': 12})
        assert result['CoverageDetails'] == json.dumps({'private_room': True, 'ambulance': True})
        assert result['IsActive'] == True
        assert result['EffectiveDate'] == date(2022, 1, 1)
        assert result['EndDate'] is None


class TestPolicy:
    """Tests for the Policy class."""
    
    def test_policy_creation(self):
        """Test creating a Policy object."""
        # Arrange
        policy_data = {
            'policy_number': 'POL12345',
            'primary_member_id': 1,
            'plan_id': 1,
            'coverage_type': 'Family',
            'start_date': date(2022, 1, 1),
            'current_premium': 300.0,
            'excess_amount': 250.0,
            'rebate_percentage': 25.0,
            'lhc_loading_percentage': 2.0
        }
        
        # Act
        policy = Policy(**policy_data)
        
        # Assert
        assert policy.policy_number == 'POL12345'
        assert policy.primary_member_id == 1
        assert policy.plan_id == 1
        assert policy.coverage_type == 'Family'
        assert policy.start_date == date(2022, 1, 1)
        assert policy.current_premium == 300.0
        assert policy.premium_frequency == 'Monthly'  # Default value
        assert policy.excess_amount == 250.0
        assert policy.rebate_percentage == 25.0
        assert policy.lhc_loading_percentage == 2.0
        assert policy.status == 'Active'  # Default value
        assert policy.payment_method == 'Direct Debit'  # Default value
        assert policy.end_date is None  # Default value
        assert policy.last_premium_paid_date is None  # Default value
        assert policy.next_premium_due_date is None  # Default value
    
    def test_policy_to_dict(self):
        """Test converting a Policy object to a dictionary."""
        # Arrange
        policy = Policy(
            policy_number='POL12345',
            primary_member_id=1,
            plan_id=1,
            coverage_type='Family',
            start_date=date(2022, 1, 1),
            current_premium=300.0,
            premium_frequency='Quarterly',
            excess_amount=250.0,
            rebate_percentage=25.0,
            lhc_loading_percentage=2.0,
            status='Active',
            payment_method='Credit Card',
            last_premium_paid_date=date(2022, 3, 1),
            next_premium_due_date=date(2022, 6, 1)
        )
        
        # Act
        result = policy.to_dict()
        
        # Assert
        assert result['PolicyNumber'] == 'POL12345'
        assert result['PrimaryMemberID'] == 1
        assert result['PlanID'] == 1
        assert result['CoverageType'] == 'Family'
        assert result['StartDate'] == date(2022, 1, 1)
        assert result['EndDate'] is None
        assert result['ExcessAmount'] == 250.0
        assert result['PremiumFrequency'] == 'Quarterly'
        assert result['CurrentPremium'] == 300.0
        assert result['RebatePercentage'] == 25.0
        assert result['LHCLoadingPercentage'] == 2.0
        assert result['Status'] == 'Active'
        assert result['PaymentMethod'] == 'Credit Card'
        assert result['LastPremiumPaidDate'] == date(2022, 3, 1)
        assert result['NextPremiumDueDate'] == date(2022, 6, 1)


class TestPolicyMember:
    """Tests for the PolicyMember class."""
    
    def test_policy_member_creation(self):
        """Test creating a PolicyMember object."""
        # Arrange
        policy_member_data = {
            'policy_id': 1,
            'member_id': 2,
            'relationship_to_primary': 'Spouse',
            'start_date': date(2022, 1, 1)
        }
        
        # Act
        policy_member = PolicyMember(**policy_member_data)
        
        # Assert
        assert policy_member.policy_id == 1
        assert policy_member.member_id == 2
        assert policy_member.relationship_to_primary == 'Spouse'
        assert policy_member.start_date == date(2022, 1, 1)
        assert policy_member.end_date is None  # Default value
        assert policy_member.is_active == True  # Default value
    
    def test_policy_member_to_dict(self):
        """Test converting a PolicyMember object to a dictionary."""
        # Arrange
        policy_member = PolicyMember(
            policy_id=1,
            member_id=2,
            relationship_to_primary='Spouse',
            start_date=date(2022, 1, 1),
            end_date=date(2022, 12, 31),
            is_active=False
        )
        
        # Act
        result = policy_member.to_dict()
        
        # Assert
        assert result['PolicyID'] == 1
        assert result['MemberID'] == 2
        assert result['RelationshipToPrimary'] == 'Spouse'
        assert result['StartDate'] == date(2022, 1, 1)
        assert result['EndDate'] == date(2022, 12, 31)
        assert result['IsActive'] == False


class TestProvider:
    """Tests for the Provider class."""
    
    def test_provider_creation(self):
        """Test creating a Provider object."""
        # Arrange
        provider_data = {
            'provider_number': 'P12345',
            'provider_name': 'Sydney Medical Center',
            'provider_type': 'Hospital',
            'address_line1': '456 Health St',
            'city': 'Sydney',
            'state': 'NSW',
            'post_code': '2000'
        }
        
        # Act
        provider = Provider(**provider_data)
        
        # Assert
        assert provider.provider_number == 'P12345'
        assert provider.provider_name == 'Sydney Medical Center'
        assert provider.provider_type == 'Hospital'
        assert provider.address_line1 == '456 Health St'
        assert provider.city == 'Sydney'
        assert provider.state == 'NSW'
        assert provider.post_code == '2000'
        assert provider.country == 'Australia'  # Default value
        assert provider.is_preferred_provider == False  # Default value
        assert provider.agreement_start_date is None  # Default value
        assert provider.agreement_end_date is None  # Default value
        assert provider.is_active == True  # Default value
    
    def test_provider_to_dict(self):
        """Test converting a Provider object to a dictionary."""
        # Arrange
        provider = Provider(
            provider_number='P12345',
            provider_name='Sydney Medical Center',
            provider_type='Hospital',
            address_line1='456 Health St',
            city='Sydney',
            state='NSW',
            post_code='2000',
            phone='0298765432',
            email='info@sydneymedical.com',
            is_preferred_provider=True,
            agreement_start_date=date(2022, 1, 1),
            agreement_end_date=date(2023, 12, 31)
        )
        
        # Act
        result = provider.to_dict()
        
        # Assert
        assert result['ProviderNumber'] == 'P12345'
        assert result['ProviderName'] == 'Sydney Medical Center'
        assert result['ProviderType'] == 'Hospital'
        assert result['AddressLine1'] == '456 Health St'
        assert result['City'] == 'Sydney'
        assert result['State'] == 'NSW'
        assert result['PostCode'] == '2000'
        assert result['Country'] == 'Australia'
        assert result['Phone'] == '0298765432'
        assert result['Email'] == 'info@sydneymedical.com'
        assert result['IsPreferredProvider'] == True
        assert result['AgreementStartDate'] == date(2022, 1, 1)
        assert result['AgreementEndDate'] == date(2023, 12, 31)
        assert result['IsActive'] == True


class TestClaim:
    """Tests for the Claim class."""
    
    def test_claim_creation(self):
        """Test creating a Claim object."""
        # Arrange
        claim_data = {
            'claim_number': 'CLM12345',
            'policy_id': 1,
            'member_id': 2,
            'provider_id': 3,
            'service_date': datetime(2022, 3, 15, 10, 30),
            'submission_date': datetime(2022, 3, 20, 14, 45),
            'claim_type': 'Hospital',
            'service_description': 'Appendectomy',
            'charged_amount': 5000.0
        }
        
        # Act
        claim = Claim(**claim_data)
        
        # Assert
        assert claim.claim_number == 'CLM12345'
        assert claim.policy_id == 1
        assert claim.member_id == 2
        assert claim.provider_id == 3
        assert claim.service_date == datetime(2022, 3, 15, 10, 30)
        assert claim.submission_date == datetime(2022, 3, 20, 14, 45)
        assert claim.claim_type == 'Hospital'
        assert claim.service_description == 'Appendectomy'
        assert claim.charged_amount == 5000.0
        assert claim.medicare_amount == 0.0  # Default value
        assert claim.insurance_amount == 0.0  # Default value
        assert claim.gap_amount == 0.0  # Default value
        assert claim.excess_applied == 0.0  # Default value
        assert claim.mbs_item_number is None  # Default value
        assert claim.status == 'Submitted'  # Default value
        assert claim.processed_date is None  # Default value
        assert claim.payment_date is None  # Default value
        assert claim.rejection_reason is None  # Default value
    
    def test_claim_to_dict(self):
        """Test converting a Claim object to a dictionary."""
        # Arrange
        service_date = datetime(2022, 3, 15, 10, 30)
        submission_date = datetime(2022, 3, 20, 14, 45)
        processed_date = datetime(2022, 3, 25, 9, 15)
        payment_date = datetime(2022, 3, 28, 11, 0)
        
        claim = Claim(
            claim_number='CLM12345',
            policy_id=1,
            member_id=2,
            provider_id=3,
            service_date=service_date,
            submission_date=submission_date,
            claim_type='Hospital',
            service_description='Appendectomy',
            charged_amount=5000.0,
            medicare_amount=2000.0,
            insurance_amount=2500.0,
            gap_amount=500.0,
            excess_applied=250.0,
            mbs_item_number='30571',
            status='Paid',
            processed_date=processed_date,
            payment_date=payment_date
        )
        
        # Act
        result = claim.to_dict()
        
        # Assert
        assert result['ClaimNumber'] == 'CLM12345'
        assert result['PolicyID'] == 1
        assert result['MemberID'] == 2
        assert result['ProviderID'] == 3
        assert result['ServiceDate'] == service_date
        assert result['SubmissionDate'] == submission_date
        assert result['ClaimType'] == 'Hospital'
        assert result['ServiceDescription'] == 'Appendectomy'
        assert result['MBSItemNumber'] == '30571'
        assert result['ChargedAmount'] == 5000.0
        assert result['MedicareAmount'] == 2000.0
        assert result['InsuranceAmount'] == 2500.0
        assert result['GapAmount'] == 500.0
        assert result['ExcessApplied'] == 250.0
        assert result['Status'] == 'Paid'
        assert result['ProcessedDate'] == processed_date
        assert result['PaymentDate'] == payment_date
        assert result['RejectionReason'] is None


class TestPremiumPayment:
    """Tests for the PremiumPayment class."""
    
    def test_premium_payment_creation(self):
        """Test creating a PremiumPayment object."""
        # Arrange
        payment_data = {
            'policy_id': 1,
            'payment_date': date(2022, 4, 1),
            'payment_amount': 300.0,
            'payment_method': 'Direct Debit',
            'period_start_date': date(2022, 4, 1),
            'period_end_date': date(2022, 4, 30)
        }
        
        # Act
        payment = PremiumPayment(**payment_data)
        
        # Assert
        assert payment.policy_id == 1
        assert payment.payment_date == date(2022, 4, 1)
        assert payment.payment_amount == 300.0
        assert payment.payment_method == 'Direct Debit'
        assert payment.period_start_date == date(2022, 4, 1)
        assert payment.period_end_date == date(2022, 4, 30)
        assert payment.payment_reference is None  # Default value
        assert payment.payment_status == 'Successful'  # Default value
    
    def test_premium_payment_to_dict(self):
        """Test converting a PremiumPayment object to a dictionary."""
        # Arrange
        payment = PremiumPayment(
            policy_id=1,
            payment_date=date(2022, 4, 1),
            payment_amount=300.0,
            payment_method='Credit Card',
            period_start_date=date(2022, 4, 1),
            period_end_date=date(2022, 4, 30),
            payment_reference='PMT-20220401-12345',
            payment_status='Successful'
        )
        
        # Act
        result = payment.to_dict()
        
        # Assert
        assert result['PolicyID'] == 1
        assert result['PaymentDate'] == date(2022, 4, 1)
        assert result['PaymentAmount'] == 300.0
        assert result['PaymentMethod'] == 'Credit Card'
        assert result['PaymentReference'] == 'PMT-20220401-12345'
        assert result['PaymentStatus'] == 'Successful'
        assert result['PeriodStartDate'] == date(2022, 4, 1)
        assert result['PeriodEndDate'] == date(2022, 4, 30)