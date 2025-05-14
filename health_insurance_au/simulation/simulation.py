"""
Main simulation module for the Health Insurance AU simulation.
"""
import random
import logging
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from health_insurance_au.utils.db_utils import (
    execute_query, execute_non_query, 
    execute_stored_procedure, bulk_insert
)
from health_insurance_au.utils.data_loader import load_sample_data, convert_to_members
from health_insurance_au.simulation.coverage_plans import generate_coverage_plans
from health_insurance_au.simulation.providers import generate_providers
from health_insurance_au.simulation.policies import generate_policies
from health_insurance_au.simulation.claims import generate_hospital_claims, generate_general_treatment_claims
from health_insurance_au.simulation.payments import generate_premium_payments
from health_insurance_au.simulation.provider_management import end_provider_agreements, update_provider_details
from health_insurance_au.models.models import (
    Member, CoveragePlan, Policy, PolicyMember, 
    Provider, Claim, PremiumPayment
)
from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

class HealthInsuranceSimulation:
    """
    Main class for the Health Insurance AU simulation.
    """
    
    def __init__(self):
        """Initialize the simulation."""
        self.members = []
        self.coverage_plans = []
        self.policies = []
        self.policy_members = []
        self.providers = []
        self.claims = []
        self.premium_payments = []
    
    def load_data_from_db(self):
        """Load existing data from the database."""
        logger.info("Loading existing data from the database...")
        
        # Load members
        members_data = execute_query("SELECT * FROM Insurance.Members")
        self.members = []
        for member_data in members_data:
            try:
                member = Member(
                    first_name=member_data['FirstName'],
                    last_name=member_data['LastName'],
                    date_of_birth=member_data['DateOfBirth'] if isinstance(member_data['DateOfBirth'], date) else datetime.strptime(member_data['DateOfBirth'], '%Y-%m-%d').date() if member_data['DateOfBirth'] else date.today(),
                    gender=member_data['Gender'],
                    address_line1=member_data['AddressLine1'],
                    city=member_data['City'],
                    state=member_data['State'],
                    post_code=member_data['PostCode'],
                    country=member_data['Country'],
                    member_number=member_data['MemberNumber'],
                    title=member_data['Title'],
                    address_line2=member_data['AddressLine2'],
                    email=member_data['Email'],
                    mobile_phone=member_data['MobilePhone'],
                    home_phone=member_data['HomePhone'],
                    medicare_number=member_data['MedicareNumber'],
                    lhc_loading_percentage=float(member_data['LHCLoadingPercentage']) if member_data['LHCLoadingPercentage'] else 0.0,
                    phi_rebate_tier=member_data['PHIRebateTier'],
                    join_date=member_data['JoinDate'] if isinstance(member_data['JoinDate'], date) else datetime.strptime(member_data['JoinDate'], '%Y-%m-%d').date() if member_data['JoinDate'] else date.today(),
                    is_active=member_data['IsActive'] == '1'
                )
                self.members.append(member)
            except Exception as e:
                logger.error(f"Error converting member data to Member object: {e}")
        
        # Load coverage plans
        plans_data = execute_query("SELECT * FROM Insurance.CoveragePlans")
        self.coverage_plans = []
        for plan_data in plans_data:
            try:
                # Parse JSON fields
                excess_options = []
                waiting_periods = {}
                coverage_details = {}
                
                if plan_data['ExcessOptions']:
                    try:
                        excess_options = json.loads(plan_data['ExcessOptions'])
                    except:
                        pass
                
                if plan_data['WaitingPeriods']:
                    try:
                        waiting_periods = json.loads(plan_data['WaitingPeriods'])
                    except:
                        pass
                
                if plan_data['CoverageDetails']:
                    try:
                        coverage_details = json.loads(plan_data['CoverageDetails'])
                    except:
                        pass
                
                plan = CoveragePlan(
                    plan_code=plan_data['PlanCode'],
                    plan_name=plan_data['PlanName'],
                    plan_type=plan_data['PlanType'],
                    monthly_premium=float(plan_data['MonthlyPremium']),
                    annual_premium=float(plan_data['AnnualPremium']),
                    effective_date=plan_data['EffectiveDate'] if isinstance(plan_data['EffectiveDate'], date) else datetime.strptime(plan_data['EffectiveDate'], '%Y-%m-%d').date() if plan_data['EffectiveDate'] else date.today(),
                    hospital_tier=plan_data['HospitalTier'],
                    excess_options=excess_options,
                    waiting_periods=waiting_periods,
                    coverage_details=coverage_details,
                    is_active=plan_data['IsActive'] == '1',
                    end_date=plan_data['EndDate'] if isinstance(plan_data['EndDate'], date) else datetime.strptime(plan_data['EndDate'], '%Y-%m-%d').date() if plan_data['EndDate'] else None
                )
                self.coverage_plans.append(plan)
            except Exception as e:
                logger.error(f"Error converting plan data to CoveragePlan object: {e}")
        
        # Load providers
        providers_data = execute_query("SELECT * FROM Insurance.Providers")
        self.providers = []
        for provider_data in providers_data:
            try:
                provider = Provider(
                    provider_number=provider_data['ProviderNumber'],
                    provider_name=provider_data['ProviderName'],
                    provider_type=provider_data['ProviderType'],
                    address_line1=provider_data['AddressLine1'],
                    city=provider_data['City'],
                    state=provider_data['State'],
                    post_code=provider_data['PostCode'],
                    country=provider_data['Country'],
                    address_line2=provider_data['AddressLine2'],
                    phone=provider_data['Phone'],
                    email=provider_data['Email'],
                    is_preferred_provider=provider_data['IsPreferredProvider'] == '1',
                    agreement_start_date=provider_data['AgreementStartDate'] if isinstance(provider_data['AgreementStartDate'], date) else datetime.strptime(provider_data['AgreementStartDate'], '%Y-%m-%d').date() if provider_data['AgreementStartDate'] else None,
                    agreement_end_date=provider_data['AgreementEndDate'] if isinstance(provider_data['AgreementEndDate'], date) else datetime.strptime(provider_data['AgreementEndDate'], '%Y-%m-%d').date() if provider_data['AgreementEndDate'] else None,
                    is_active=provider_data['IsActive'] == '1'
                )
                self.providers.append(provider)
            except Exception as e:
                logger.error(f"Error converting provider data to Provider object: {e}")
        
        logger.info(f"Loaded {len(self.members)} members, {len(self.coverage_plans)} coverage plans, and {len(self.providers)} providers from database")
    
    def add_members(self, count: int = 10, simulation_date: Optional[date] = None):
        """
        Add new members to the database.
        
        Args:
            count: Number of members to add
            simulation_date: The date to use for LastModified
        """
        logger.info(f"Adding {count} new members...")
        
        # Load sample data
        sample_data = load_sample_data()
        if not sample_data:
            logger.error("Failed to load sample data")
            return
        
        # Convert to Member objects
        new_members = convert_to_members(sample_data, count)
        if not new_members:
            logger.error("Failed to convert sample data to Member objects")
            return
        
        # Insert into database
        member_dicts = [member.to_dict() for member in new_members]
        try:
            rows_affected = bulk_insert("Insurance.Members", member_dicts, simulation_date)
            logger.info(f"Added {rows_affected} new members to the database")
            
            # Add to in-memory collection
            self.members.extend(new_members)
        except Exception as e:
            logger.error(f"Error adding members to database: {e}")
    
    def add_coverage_plans(self, count: int = 5, simulation_date: Optional[date] = None):
        """
        Add new coverage plans to the database.
        
        Args:
            count: Number of plans to add
            simulation_date: The date to use for LastModified
        """
        logger.info(f"Adding {count} new coverage plans...")
        
        # Generate coverage plans
        new_plans = generate_coverage_plans(count)
        if not new_plans:
            logger.error("Failed to generate coverage plans")
            return
        
        # Insert into database
        plan_dicts = [plan.to_dict() for plan in new_plans]
        try:
            rows_affected = bulk_insert("Insurance.CoveragePlans", plan_dicts, simulation_date)
            logger.info(f"Added {rows_affected} new coverage plans to the database")
            
            # Add to in-memory collection
            self.coverage_plans.extend(new_plans)
        except Exception as e:
            logger.error(f"Error adding coverage plans to database: {e}")
    
    def add_providers(self, count: int = 20, simulation_date: Optional[date] = None):
        """
        Add new providers to the database.
        
        Args:
            count: Number of providers to add
            simulation_date: The date to use for LastModified
        """
        logger.info(f"Adding {count} new providers...")
        
        # Generate providers
        new_providers = generate_providers(count)
        if not new_providers:
            logger.error("Failed to generate providers")
            return
        
        # Insert into database
        provider_dicts = [provider.to_dict() for provider in new_providers]
        try:
            rows_affected = bulk_insert("Insurance.Providers", provider_dicts, simulation_date)
            logger.info(f"Added {rows_affected} new providers to the database")
            
            # Add to in-memory collection
            self.providers.extend(new_providers)
        except Exception as e:
            logger.error(f"Error adding providers to database: {e}")
    
    def create_new_policies(self, count: int = 10, simulation_date: Optional[date] = None):
        """
        Create new policies for members.
        
        Args:
            count: Number of policies to create
            simulation_date: The date to use for LastModified
        """
        logger.info(f"Creating {count} new policies...")
        
        if not self.members or not self.coverage_plans:
            logger.error("No members or coverage plans available to create policies")
            return
        
        # Generate policies
        new_policies, new_policy_members = generate_policies(self.members, self.coverage_plans, count)
        if not new_policies:
            logger.error("Failed to generate policies")
            return
        
        # Insert policies into database
        policy_dicts = [policy.to_dict() for policy in new_policies]
        try:
            rows_affected = bulk_insert("Insurance.Policies", policy_dicts, simulation_date)
            logger.info(f"Added {rows_affected} new policies to the database")
            
            # Add to in-memory collection
            self.policies.extend(new_policies)
        except Exception as e:
            logger.error(f"Error adding policies to database: {e}")
            return
        
        # Insert policy members into database
        policy_member_dicts = [pm.to_dict() for pm in new_policy_members]
        try:
            rows_affected = bulk_insert("Insurance.PolicyMembers", policy_member_dicts, simulation_date)
            logger.info(f"Added {rows_affected} new policy members to the database")
            
            # Add to in-memory collection
            self.policy_members.extend(new_policy_members)
        except Exception as e:
            logger.error(f"Error adding policy members to database: {e}")
    
    def update_members(self, percentage: float = 5.0, simulation_date: Optional[date] = None):
        """
        Update a percentage of members with new information.
        
        Args:
            percentage: Percentage of members to update
            simulation_date: The date to use for LastModified
        """
        logger.info(f"Updating approximately {percentage}% of members...")
        
        if not self.members:
            logger.error("No members available to update")
            return
        
        # Calculate number of members to update
        count = max(1, int(len(self.members) * percentage / 100))
        
        # Select random members to update
        members_to_update = random.sample(self.members, count)
        
        for member in members_to_update:
            # Make random changes
            change_type = random.choice(['contact', 'address', 'both'])
            
            if change_type in ['contact', 'both']:
                # Update contact information
                member.email = f"updated_{member.first_name.lower()}.{member.last_name.lower()}@example.com"
                member.mobile_phone = f"04{random.randint(10, 99)}{random.randint(100000, 999999)}"
            
            if change_type in ['address', 'both']:
                # Update address
                member.address_line1 = f"{random.randint(1, 999)} New {random.choice(['Street', 'Road', 'Avenue', 'Boulevard'])}"
                # Keep the same city and state
            
            # Update the database
            try:
                query = """
                UPDATE Insurance.Members
                SET Email = ?, MobilePhone = ?, AddressLine1 = ?, LastModified = GETDATE()
                WHERE MemberNumber = ?
                """
                execute_non_query(query, (member.email, member.mobile_phone, member.address_line1, member.member_number), simulation_date)
            except Exception as e:
                logger.error(f"Error updating member {member.member_number}: {e}")
        
        logger.info(f"Updated {len(members_to_update)} members")
    
    def process_policy_changes(self, percentage: float = 2.0, simulation_date: Optional[date] = None):
        """
        Process changes to a percentage of policies.
        
        Args:
            percentage: Percentage of policies to change
            simulation_date: The date to use for LastModified
        """
        logger.info(f"Processing changes for approximately {percentage}% of policies...")
        
        if not self.policies:
            logger.error("No policies available to change")
            return
        
        # Calculate number of policies to change
        count = max(1, int(len(self.policies) * percentage / 100))
        
        # Select random policies to change
        policies_to_change = random.sample(self.policies, count)
        
        for policy in policies_to_change:
            # Make random changes
            change_type = random.choice(['plan', 'coverage_type', 'excess', 'status', 'payment_method'])
            
            if change_type == 'plan' and self.coverage_plans:
                # Change to a different plan
                new_plan = random.choice(self.coverage_plans)
                policy.plan_id = self.coverage_plans.index(new_plan) + 1
                policy.current_premium = new_plan.monthly_premium
            elif change_type == 'coverage_type':
                # Change coverage type
                policy.coverage_type = random.choice(['Single', 'Couple', 'Family', 'Single Parent'])
            elif change_type == 'excess':
                # Change excess amount
                policy.excess_amount = random.choice([0, 250, 500, 750])
            elif change_type == 'status':
                # Change status
                policy.status = random.choice(['Active', 'Suspended', 'Cancelled'])
            elif change_type == 'payment_method':
                # Change payment method
                policy.payment_method = random.choice(['Direct Debit', 'Credit Card', 'BPAY', 'PayPal'])
            
            # Update the database
            try:
                query = """
                UPDATE Insurance.Policies
                SET PlanID = ?, CoverageType = ?, ExcessAmount = ?, Status = ?, 
                    PaymentMethod = ?, CurrentPremium = ?, LastModified = GETDATE()
                WHERE PolicyNumber = ?
                """
                execute_non_query(query, (
                    policy.plan_id, 
                    policy.coverage_type, 
                    policy.excess_amount, 
                    policy.status, 
                    policy.payment_method, 
                    policy.current_premium, 
                    policy.policy_number
                ), simulation_date)
            except Exception as e:
                logger.error(f"Error updating policy {policy.policy_number}: {e}")
        
        logger.info(f"Processed changes for {len(policies_to_change)} policies")
    
    def generate_hospital_claims(self, count: int = 5, simulation_date: Optional[date] = None):
        """
        Generate hospital claims.
        
        Args:
            count: Number of claims to generate
            simulation_date: The date to use for LastModified
        """
        logger.info(f"Generating {count} hospital claims...")
        
        if not self.policies or not self.members or not self.providers:
            logger.error("No policies, members, or providers available to generate claims")
            return
        
        # Generate claims
        new_claims = generate_hospital_claims(self.policies, self.members, self.providers, count)
        if not new_claims:
            logger.error("Failed to generate hospital claims")
            return
        
        # Insert into database
        claim_dicts = [claim.to_dict() for claim in new_claims]
        try:
            rows_affected = bulk_insert("Insurance.Claims", claim_dicts, simulation_date)
            logger.info(f"Added {rows_affected} new hospital claims to the database")
            
            # Add to in-memory collection
            self.claims.extend(new_claims)
        except Exception as e:
            logger.error(f"Error adding hospital claims to database: {e}")
    
    def generate_general_treatment_claims(self, count: int = 15, simulation_date: Optional[date] = None):
        """
        Generate general treatment claims.
        
        Args:
            count: Number of claims to generate
            simulation_date: The date to use for LastModified
        """
        logger.info(f"Generating {count} general treatment claims...")
        
        if not self.policies or not self.members or not self.providers:
            logger.error("No policies, members, or providers available to generate claims")
            return
        
        # Generate claims
        new_claims = generate_general_treatment_claims(self.policies, self.members, self.providers, count)
        if not new_claims:
            logger.error("Failed to generate general treatment claims")
            return
        
        # Insert into database
        claim_dicts = [claim.to_dict() for claim in new_claims]
        try:
            rows_affected = bulk_insert("Insurance.Claims", claim_dicts, simulation_date)
            logger.info(f"Added {rows_affected} new general treatment claims to the database")
            
            # Add to in-memory collection
            self.claims.extend(new_claims)
        except Exception as e:
            logger.error(f"Error adding general treatment claims to database: {e}")
    
    def process_premium_payments(self, simulation_date: date = None):
        """
        Process premium payments for policies due on the simulation date.
        
        Args:
            simulation_date: The date to process payments for
        """
        if simulation_date is None:
            simulation_date = date.today()
            
        logger.info(f"Processing premium payments for {simulation_date}...")
        
        if not self.policies:
            logger.error("No policies available to process payments")
            return
        
        # Generate payments
        new_payments = generate_premium_payments(self.policies, simulation_date)
        if not new_payments:
            logger.info("No premium payments due on this date")
            return
        
        # Insert into database
        payment_dicts = [payment.to_dict() for payment in new_payments]
        try:
            rows_affected = bulk_insert("Insurance.PremiumPayments", payment_dicts, simulation_date)
            logger.info(f"Added {rows_affected} new premium payments to the database")
            
            # Add to in-memory collection
            self.premium_payments.extend(new_payments)
            
            # Update policies with new payment dates
            for policy in self.policies:
                if policy.next_premium_due_date and policy.next_premium_due_date <= simulation_date:
                    try:
                        query = """
                        UPDATE Insurance.Policies
                        SET LastPremiumPaidDate = ?, NextPremiumDueDate = ?, LastModified = GETDATE()
                        WHERE PolicyNumber = ?
                        """
                        execute_non_query(query, (
                            policy.last_premium_paid_date, 
                            policy.next_premium_due_date, 
                            policy.policy_number
                        ), simulation_date)
                    except Exception as e:
                        logger.error(f"Error updating policy {policy.policy_number} payment dates: {e}")
        except Exception as e:
            logger.error(f"Error adding premium payments to database: {e}")
    
    def process_claim_assessments(self, percentage: float = 80.0, simulation_date: Optional[date] = None):
        """
        Process a percentage of submitted claims.
        
        Args:
            percentage: Percentage of submitted claims to process
            simulation_date: The date to use for LastModified
        """
        logger.info(f"Processing approximately {percentage}% of submitted claims...")
        
        # Get submitted claims from database
        submitted_claims = execute_query("""
            SELECT * FROM Insurance.Claims 
            WHERE Status = 'Submitted' OR Status = 'In Process'
        """)
        
        if not submitted_claims:
            logger.info("No submitted claims to process")
            return
        
        # Calculate number of claims to process
        count = max(1, int(len(submitted_claims) * percentage / 100))
        
        # Select random claims to process
        claims_to_process = random.sample(submitted_claims, min(count, len(submitted_claims)))
        
        for claim in claims_to_process:
            # Determine new status
            new_status = random.choices(
                ['Approved', 'Paid', 'Rejected'],
                weights=[0.2, 0.7, 0.1],
                k=1
            )[0]
            
            # Set processed date
            processed_date = simulation_date if simulation_date else date.today()
            
            # Set payment date and rejection reason
            payment_date = None
            rejection_reason = None
            
            if new_status == 'Paid':
                payment_date = processed_date + timedelta(days=random.randint(1, 3))
            elif new_status == 'Rejected':
                rejection_reasons = [
                    'Service not covered by policy',
                    'Annual limit reached',
                    'Waiting period not served',
                    'Insufficient documentation',
                    'Duplicate claim'
                ]
                rejection_reason = random.choice(rejection_reasons)
            
            # Update the database
            try:
                query = """
                UPDATE Insurance.Claims
                SET Status = ?, ProcessedDate = ?, PaymentDate = ?, RejectionReason = ?, LastModified = GETDATE()
                WHERE ClaimNumber = ?
                """
                execute_non_query(query, (
                    new_status, 
                    processed_date, 
                    payment_date, 
                    rejection_reason, 
                    claim['ClaimNumber']
                ), simulation_date)
            except Exception as e:
                logger.error(f"Error updating claim {claim['ClaimNumber']}: {e}")
        
        logger.info(f"Processed {len(claims_to_process)} claims")
    
    def run_daily_simulation(
        self,
        simulation_date: date = None,
        add_new_members: bool = True,
        new_members_count: int = 5,
        add_new_plans: bool = False,
        new_plans_count: int = 0,
        add_new_providers: bool = True,
        new_providers_count: int = 5,
        create_new_policies: bool = True,
        new_policies_count: int = 3,
        update_members: bool = True,
        member_update_percentage: float = 2.0,
        update_providers: bool = True,
        provider_update_percentage: float = 5.0,
        end_provider_agreements: bool = True,
        provider_agreement_end_percentage: float = 1.0,
        process_policy_changes: bool = True,
        policy_change_percentage: float = 1.0,
        generate_hospital_claims: bool = True,
        hospital_claims_count: int = 3,
        generate_general_claims: bool = True,
        general_claims_count: int = 10,
        process_premium_payments: bool = True,
        process_claims: bool = True,
        claim_process_percentage: float = 80.0
    ):
        """
        Run a daily simulation with the specified parameters.
        
        Args:
            simulation_date: The date to simulate (default: today)
            add_new_members: Whether to add new members
            new_members_count: Number of new members to add
            add_new_plans: Whether to add new coverage plans
            new_plans_count: Number of new plans to add
            add_new_providers: Whether to add new providers
            new_providers_count: Number of new providers to add
            create_new_policies: Whether to create new policies
            new_policies_count: Number of new policies to create
            update_members: Whether to update existing members
            member_update_percentage: Percentage of members to update
            update_providers: Whether to update provider details
            provider_update_percentage: Percentage of providers to update
            end_provider_agreements: Whether to end provider agreements
            provider_agreement_end_percentage: Percentage of provider agreements to end
            process_policy_changes: Whether to process policy changes
            policy_change_percentage: Percentage of policies to change
            generate_hospital_claims: Whether to generate hospital claims
            hospital_claims_count: Number of hospital claims to generate
            generate_general_claims: Whether to generate general treatment claims
            general_claims_count: Number of general treatment claims to generate
            process_premium_payments: Whether to process premium payments
            process_claims: Whether to process claim assessments
            claim_process_percentage: Percentage of claims to process
        """
        if simulation_date is None:
            simulation_date = date.today()
            
        logger.info(f"Running daily simulation for {simulation_date}...")
        
        # Load existing data from the database
        self.load_data_from_db()
        
        # Add new members if requested
        if add_new_members:
            self.add_members(new_members_count, simulation_date)
        
        # Add new coverage plans if requested
        if add_new_plans:
            self.add_coverage_plans(new_plans_count, simulation_date)
            
        # Add new providers if requested
        if add_new_providers:
            self.add_providers(new_providers_count, simulation_date)
        
        # Create new policies if requested
        if create_new_policies:
            self.create_new_policies(new_policies_count, simulation_date)
        
        # Update members if requested
        if update_members:
            self.update_members(member_update_percentage, simulation_date)
            
        # Update providers if requested
        if update_providers:
            from health_insurance_au.simulation.provider_management import update_provider_details
            update_provider_details(provider_update_percentage, simulation_date)
            
        # End provider agreements if requested
        if end_provider_agreements:
            from health_insurance_au.simulation.provider_management import end_provider_agreements
            end_provider_agreements(provider_agreement_end_percentage, simulation_date)
        
        # Process policy changes if requested
        if process_policy_changes:
            self.process_policy_changes(policy_change_percentage, simulation_date)
        
        # Generate hospital claims if requested
        if generate_hospital_claims:
            self.generate_hospital_claims(hospital_claims_count, simulation_date)
        
        # Generate general treatment claims if requested
        if generate_general_claims:
            self.generate_general_treatment_claims(general_claims_count, simulation_date)
        
        # Process premium payments if requested
        if process_premium_payments:
            self.process_premium_payments(simulation_date)
        
        # Process claims if requested
        if process_claims:
            self.process_claim_assessments(claim_process_percentage, simulation_date)
        
        logger.info(f"Daily simulation completed for {simulation_date}")
    
    def run_historical_simulation(
        self,
        start_date: date,
        end_date: date = None,
        frequency: str = 'daily'
    ):
        """
        Run a historical simulation from start_date to end_date.
        
        Args:
            start_date: The start date for the simulation
            end_date: The end date for the simulation (default: today)
            frequency: The frequency of simulation runs ('daily', 'weekly', 'monthly')
        """
        if end_date is None:
            end_date = date.today()
            
        logger.info(f"Running historical simulation from {start_date} to {end_date} with {frequency} frequency...")
        
        # # Initialize with some base data
        # # Add initial members
        # self.add_members(100)
        
        # # Add providers
        # self.add_providers(50)
        
        # # Add coverage plans
        # self.add_coverage_plans(15)
        
        # # Create initial policies
        # self.create_new_policies(50)
        
        # Determine the date increment based on frequency
        if frequency == 'daily':
            date_increment = timedelta(days=1)
        elif frequency == 'weekly':
            date_increment = timedelta(days=7)
        elif frequency == 'monthly':
            date_increment = timedelta(days=30)
        else:
            logger.error(f"Invalid frequency: {frequency}")
            return
        
        # Run the simulation for each date
        current_date = start_date
        while current_date <= end_date:
            # Vary the parameters slightly for each run to create more realistic data
            self.run_daily_simulation(
                simulation_date=current_date,
                add_new_members=random.random() < 0.7,  # 70% chance of adding new members
                new_members_count=random.randint(1, 10),
                add_new_plans=random.random() < 0.05,  # 5% chance of adding new plans
                new_plans_count=random.randint(1, 3) if random.random() < 0.05 else 0,
                create_new_policies=random.random() < 0.8,  # 80% chance of creating new policies
                new_policies_count=random.randint(1, 8),
                update_members=random.random() < 0.6,  # 60% chance of updating members
                member_update_percentage=random.uniform(1.0, 5.0),
                process_policy_changes=random.random() < 0.4,  # 40% chance of processing policy changes
                policy_change_percentage=random.uniform(0.5, 3.0),
                generate_hospital_claims=random.random() < 0.9,  # 90% chance of generating hospital claims
                hospital_claims_count=random.randint(1, 10),
                generate_general_claims=random.random() < 0.95,  # 95% chance of generating general claims
                general_claims_count=random.randint(5, 30),
                process_premium_payments=True,  # Always process premium payments
                process_claims=random.random() < 0.8,  # 80% chance of processing claims
                claim_process_percentage=random.uniform(70.0, 95.0)
            )
            
            # Increment the date
            current_date += date_increment
        
        logger.info(f"Historical simulation completed from {start_date} to {end_date}")