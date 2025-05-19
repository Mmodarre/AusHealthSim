"""
Claim pattern generation module for the Health Insurance AU simulation.
"""
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from health_insurance_au.models.models import Claim, Member, Provider
from health_insurance_au.utils.db_utils import execute_query, bulk_insert
from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

class ClaimPatternGenerator:
    """
    Class for generating claims with realistic distributions and patterns.
    """
    
    def __init__(self):
        """Initialize the claim pattern generator."""
        # Define claim type distributions
        self.claim_type_distribution = {
            'Hospital': 0.15,
            'General Treatment': 0.65,
            'Specialist': 0.20
        }
        
        # Define service type distributions
        self.service_type_distribution = {
            'Hospital': {
                'Accommodation': 0.3,
                'Theatre': 0.25,
                'Prosthesis': 0.15,
                'Pharmacy': 0.2,
                'Pathology': 0.1
            },
            'General Treatment': {
                'Dental': 0.3,
                'Optical': 0.25,
                'Physiotherapy': 0.2,
                'Chiropractic': 0.15,
                'Psychology': 0.1
            },
            'Specialist': {
                'Cardiology': 0.2,
                'Dermatology': 0.15,
                'Orthopedic': 0.2,
                'Neurology': 0.15,
                'Gastroenterology': 0.15,
                'Endocrinology': 0.1,
                'Ophthalmology': 0.05
            }
        }
        
        # Define amount distributions by service type
        self.amount_distributions = {
            'Hospital': {
                'Accommodation': (500.0, 2000.0),
                'Theatre': (1000.0, 5000.0),
                'Prosthesis': (800.0, 10000.0),
                'Pharmacy': (100.0, 500.0),
                'Pathology': (200.0, 800.0)
            },
            'General Treatment': {
                'Dental': (80.0, 500.0),
                'Optical': (200.0, 600.0),
                'Physiotherapy': (70.0, 150.0),
                'Chiropractic': (70.0, 150.0),
                'Psychology': (150.0, 300.0)
            },
            'Specialist': {
                'Cardiology': (200.0, 800.0),
                'Dermatology': (150.0, 400.0),
                'Orthopedic': (200.0, 1000.0),
                'Neurology': (200.0, 800.0),
                'Gastroenterology': (200.0, 600.0),
                'Endocrinology': (180.0, 500.0),
                'Ophthalmology': (150.0, 600.0)
            }
        }
        
        # Define MBS item numbers by service type
        self.mbs_item_numbers = {
            'Hospital': {
                'Accommodation': ['11000', '11001', '11002'],
                'Theatre': ['51300', '51303', '51306'],
                'Prosthesis': ['38483', '38484', '38488'],
                'Pharmacy': ['11600', '11601', '11603'],
                'Pathology': ['73801', '73802', '73803']
            },
            'General Treatment': {
                'Dental': ['85511', '85512', '85521'],
                'Optical': ['91001', '91002', '91003'],
                'Physiotherapy': ['10960', '10961', '10962'],
                'Chiropractic': ['10964', '10965', '10966'],
                'Psychology': ['80000', '80001', '80010']
            },
            'Specialist': {
                'Cardiology': ['11700', '11701', '11702'],
                'Dermatology': ['30071', '30072', '30073'],
                'Orthopedic': ['49318', '49319', '49320'],
                'Neurology': ['11012', '11015', '11018'],
                'Gastroenterology': ['30473', '30476', '30478'],
                'Endocrinology': ['66500', '66503', '66506'],
                'Ophthalmology': ['42503', '42506', '42509']
            }
        }
    
    def _select_weighted_random(self, distribution: Dict[str, float]) -> str:
        """
        Select a random item based on weighted distribution.
        
        Args:
            distribution: Dictionary of items and their weights
            
        Returns:
            Selected item
        """
        items = list(distribution.keys())
        weights = list(distribution.values())
        return random.choices(items, weights=weights, k=1)[0]
    
    def generate_enhanced_claims(self, members: List[Member], providers: List[Provider], count: int, simulation_date: date = None) -> List[Claim]:
        """
        Generate enhanced claims with realistic patterns.
        
        Args:
            members: List of members to generate claims for
            providers: List of providers to generate claims for
            count: Number of claims to generate
            simulation_date: The simulation date
            
        Returns:
            A list of generated Claim objects
        """
        if simulation_date is None:
            simulation_date = date.today()
        
        claims = []
        
        # Create a mapping of provider types
        provider_types = {}
        for provider in providers:
            provider_type = provider.provider_type
            if provider_type not in provider_types:
                provider_types[provider_type] = []
            provider_types[provider_type].append(provider)
        
        for _ in range(count):
            # Select a random claim type based on distribution
            claim_type = self._select_weighted_random(self.claim_type_distribution)
            
            # Select a random service type based on claim type
            service_type = self._select_weighted_random(self.service_type_distribution[claim_type])
            
            # Select a random member
            member = random.choice(members)
            member_id = getattr(member, 'member_id', 0)
            
            # Find policies for this member
            # For simplicity, we'll use a random policy ID between 1 and 100
            # In a real implementation, you would query the database for the member's policies
            policy_id = random.randint(1, 100)
            
            # Select an appropriate provider based on service type
            provider_type_mapping = {
                'Dental': 'Dental',
                'Optical': 'Optical',
                'Physiotherapy': 'Physiotherapy',
                'Chiropractic': 'Chiropractic',
                'Psychology': 'Psychology',
                'Accommodation': 'Hospital',
                'Theatre': 'Hospital',
                'Prosthesis': 'Hospital',
                'Pharmacy': 'Hospital',
                'Pathology': 'Hospital',
                'Cardiology': 'Specialist',
                'Dermatology': 'Specialist',
                'Orthopedic': 'Specialist',
                'Neurology': 'Specialist',
                'Gastroenterology': 'Specialist',
                'Endocrinology': 'Specialist',
                'Ophthalmology': 'Specialist'
            }
            
            # Find a provider of the appropriate type if available
            matching_provider_type = provider_type_mapping.get(service_type, 'General Practitioner')
            matching_providers = provider_types.get(matching_provider_type, [])
            
            if matching_providers:
                provider = random.choice(matching_providers)
            else:
                # If no matching provider, use any provider
                provider = random.choice(providers)
            
            provider_id = getattr(provider, 'provider_id', 0)
            
            # Generate claim details
            service_date = simulation_date - timedelta(days=random.randint(0, 30))
            submission_date = service_date + timedelta(days=random.randint(1, 14))
            
            # Generate amounts based on service type
            min_amount, max_amount = self.amount_distributions[claim_type][service_type]
            charged_amount = round(random.uniform(min_amount, max_amount), 2)
            
            # Calculate Medicare and insurance amounts
            if claim_type == 'Hospital':
                medicare_amount = round(charged_amount * random.uniform(0.5, 0.75), 2)
                insurance_amount = round(charged_amount * random.uniform(0.1, 0.4), 2)
            else:
                medicare_amount = round(charged_amount * random.uniform(0.0, 0.5), 2)
                insurance_amount = round(charged_amount * random.uniform(0.3, 0.8), 2)
            
            gap_amount = max(0, charged_amount - medicare_amount - insurance_amount)
            
            # Select an MBS item number if available
            mbs_item_number = None
            if service_type in self.mbs_item_numbers.get(claim_type, {}):
                mbs_item_number = random.choice(self.mbs_item_numbers[claim_type][service_type])
            
            # Generate a claim number
            claim_number = f"CLM-{simulation_date.strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
            
            # Create the claim
            claim = Claim(
                claim_number=claim_number,
                policy_id=policy_id,
                member_id=member_id,
                provider_id=provider_id,
                service_date=datetime.combine(service_date, datetime.min.time()),
                submission_date=datetime.combine(submission_date, datetime.min.time()),
                claim_type=claim_type,
                service_description=f"{service_type} Service",
                charged_amount=charged_amount,
                medicare_amount=medicare_amount,
                insurance_amount=insurance_amount,
                gap_amount=gap_amount,
                excess_applied=0.0,
                mbs_item_number=mbs_item_number,
                status="Submitted"
            )
            
            # Add enhanced attributes for a small percentage of claims
            if random.random() < 0.1:  # 10% of claims get anomaly attributes
                claim.anomaly_score = round(random.uniform(0.5, 0.95), 2)
                claim.fraud_indicator_count = random.randint(1, 3)
                claim.unusual_pattern_flag = random.random() < 0.7
                claim.claim_complexity_score = round(random.uniform(0.3, 0.8), 2)
                claim.review_flag = random.random() < 0.8
            else:
                claim.anomaly_score = round(random.uniform(0.0, 0.3), 2)
                claim.fraud_indicator_count = 0
                claim.unusual_pattern_flag = False
                claim.claim_complexity_score = round(random.uniform(0.1, 0.5), 2)
                claim.review_flag = False
            
            claims.append(claim)
        
        logger.info(f"Generated {len(claims)} enhanced claims")
        return claims
    
    def generate_claim_clusters(self, members: List[Member], providers: List[Provider], simulation_date: date = None) -> List[Claim]:
        """
        Generate clusters of related claims to create patterns.
        
        Args:
            members: List of members to generate claims for
            providers: List of providers to generate claims for
            simulation_date: The simulation date
            
        Returns:
            A list of generated Claim objects
        """
        if simulation_date is None:
            simulation_date = date.today()
        
        claims = []
        
        # Generate a few claim clusters
        cluster_count = random.randint(3, 8)
        
        for _ in range(cluster_count):
            # Select a random member and provider
            member = random.choice(members)
            provider = random.choice(providers)
            member_id = getattr(member, 'member_id', 0)
            provider_id = getattr(provider, 'provider_id', 0)
            
            # For simplicity, use a random policy ID
            policy_id = random.randint(1, 100)
            
            # Select a random claim type and service type
            claim_type = self._select_weighted_random(self.claim_type_distribution)
            service_type = self._select_weighted_random(self.service_type_distribution[claim_type])
            
            # Generate a cluster of claims with similar characteristics
            cluster_size = random.randint(3, 8)
            
            # Define the pattern type
            pattern_type = random.choice([
                'frequency',  # Multiple claims in a short period
                'amount',     # Similar amounts
                'service'     # Same service type
            ])
            
            for i in range(cluster_size):
                # Generate a claim number
                claim_number = f"CLM-{simulation_date.strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
                
                # Set dates based on pattern type
                if pattern_type == 'frequency':
                    # Claims close together in time
                    service_date = simulation_date - timedelta(days=random.randint(1, 10))
                else:
                    # More spread out
                    service_date = simulation_date - timedelta(days=random.randint(5, 60))
                
                submission_date = service_date + timedelta(days=random.randint(1, 7))
                
                # Set amounts based on pattern type
                min_amount, max_amount = self.amount_distributions[claim_type][service_type]
                
                if pattern_type == 'amount':
                    # Similar amounts
                    base_amount = random.uniform(min_amount, max_amount)
                    variation = base_amount * 0.05  # 5% variation
                    charged_amount = round(base_amount + random.uniform(-variation, variation), 2)
                else:
                    # Normal amount distribution
                    charged_amount = round(random.uniform(min_amount, max_amount), 2)
                
                # Calculate Medicare and insurance amounts
                medicare_amount = round(charged_amount * random.uniform(0.0, 0.6), 2)
                insurance_amount = round(charged_amount * random.uniform(0.2, 0.8), 2)
                gap_amount = max(0, charged_amount - medicare_amount - insurance_amount)
                
                # Select an MBS item number if available
                mbs_item_number = None
                if service_type in self.mbs_item_numbers.get(claim_type, {}):
                    mbs_item_number = random.choice(self.mbs_item_numbers[claim_type][service_type])
                
                # Create the claim
                claim = Claim(
                    claim_number=claim_number,
                    policy_id=policy_id,
                    member_id=member_id,
                    provider_id=provider_id,
                    service_date=datetime.combine(service_date, datetime.min.time()),
                    submission_date=datetime.combine(submission_date, datetime.min.time()),
                    claim_type=claim_type,
                    service_description=f"{service_type} Service",
                    charged_amount=charged_amount,
                    medicare_amount=medicare_amount,
                    insurance_amount=insurance_amount,
                    gap_amount=gap_amount,
                    excess_applied=0.0,
                    mbs_item_number=mbs_item_number,
                    status="Submitted"
                )
                
                # Add enhanced attributes - these claims are part of a pattern
                claim.anomaly_score = round(random.uniform(0.4, 0.7), 2)
                claim.fraud_indicator_count = random.randint(0, 2)
                claim.unusual_pattern_flag = random.random() < 0.5
                claim.claim_complexity_score = round(random.uniform(0.2, 0.6), 2)
                claim.review_flag = random.random() < 0.3
                
                claims.append(claim)
        
        logger.info(f"Generated {len(claims)} claims in {cluster_count} clusters")
        return claims