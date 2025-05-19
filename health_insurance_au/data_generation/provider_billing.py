"""
Provider billing pattern generation module for the Health Insurance AU simulation.
"""
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from health_insurance_au.models.models import Provider, Claim
from health_insurance_au.utils.db_utils import execute_query, execute_non_query, bulk_insert
from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

class ProviderBillingGenerator:
    """
    Class for generating varied provider billing patterns.
    """
    
    def __init__(self):
        """Initialize the provider billing generator."""
        # Define provider types and their billing characteristics
        self.provider_billing_profiles = {
            'General Practitioner': {
                'avg_claim_range': (80.0, 150.0),
                'frequency_ratings': ['Low', 'Medium', 'Medium', 'High'],
                'risk_factor_range': (0.1, 0.4),
                'compliance_score_range': (0.7, 0.95)
            },
            'Specialist': {
                'avg_claim_range': (200.0, 500.0),
                'frequency_ratings': ['Low', 'Low', 'Medium', 'Medium', 'High'],
                'risk_factor_range': (0.2, 0.6),
                'compliance_score_range': (0.65, 0.9)
            },
            'Hospital': {
                'avg_claim_range': (1000.0, 5000.0),
                'frequency_ratings': ['Low', 'Medium', 'High'],
                'risk_factor_range': (0.3, 0.7),
                'compliance_score_range': (0.6, 0.85)
            },
            'Dental': {
                'avg_claim_range': (120.0, 350.0),
                'frequency_ratings': ['Medium', 'Medium', 'High'],
                'risk_factor_range': (0.2, 0.5),
                'compliance_score_range': (0.7, 0.9)
            },
            'Physiotherapy': {
                'avg_claim_range': (90.0, 180.0),
                'frequency_ratings': ['Medium', 'High', 'High'],
                'risk_factor_range': (0.15, 0.45),
                'compliance_score_range': (0.75, 0.95)
            },
            'Optical': {
                'avg_claim_range': (200.0, 600.0),
                'frequency_ratings': ['Low', 'Low', 'Medium'],
                'risk_factor_range': (0.1, 0.3),
                'compliance_score_range': (0.8, 0.98)
            },
            'Chiropractic': {
                'avg_claim_range': (70.0, 150.0),
                'frequency_ratings': ['Medium', 'High'],
                'risk_factor_range': (0.2, 0.5),
                'compliance_score_range': (0.7, 0.9)
            },
            'Psychology': {
                'avg_claim_range': (150.0, 300.0),
                'frequency_ratings': ['Low', 'Medium'],
                'risk_factor_range': (0.1, 0.4),
                'compliance_score_range': (0.8, 0.95)
            }
        }
        
        # Default profile for unknown provider types
        self.default_profile = {
            'avg_claim_range': (100.0, 300.0),
            'frequency_ratings': ['Low', 'Medium', 'High'],
            'risk_factor_range': (0.2, 0.5),
            'compliance_score_range': (0.7, 0.9)
        }
    
    def generate_provider_billing_attributes(self, providers: List[Provider], claims: List[Claim] = None) -> List[Provider]:
        """
        Generate billing pattern attributes for providers.
        
        Args:
            providers: List of providers to generate attributes for
            claims: Optional list of claims to use for calculating actual averages
            
        Returns:
            The updated list of providers with billing attributes
        """
        if not providers:
            return providers
        
        # Calculate actual average claim values if claims are provided
        provider_claim_averages = {}
        if claims:
            provider_claims = {}
            for claim in claims:
                provider_id = claim.provider_id
                if provider_id not in provider_claims:
                    provider_claims[provider_id] = []
                provider_claims[provider_id].append(claim.charged_amount)
            
            for provider_id, claim_amounts in provider_claims.items():
                if claim_amounts:
                    provider_claim_averages[provider_id] = sum(claim_amounts) / len(claim_amounts)
        
        for provider in providers:
            # Get the appropriate billing profile based on provider type
            provider_type = provider.provider_type
            profile = self.provider_billing_profiles.get(provider_type, self.default_profile)
            
            # Generate billing pattern score (0.0 to 1.0)
            # Higher scores indicate more consistent billing patterns
            provider.billing_pattern_score = round(random.uniform(0.3, 0.95), 2)
            
            # Set average claim value
            provider_id = getattr(provider, 'provider_id', 0)
            if provider_id in provider_claim_averages:
                # Use actual average if available
                provider.avg_claim_value = round(provider_claim_averages[provider_id], 2)
            else:
                # Generate a random average within the appropriate range
                min_avg, max_avg = profile['avg_claim_range']
                provider.avg_claim_value = round(random.uniform(min_avg, max_avg), 2)
            
            # Set claim frequency rating
            provider.claim_frequency_rating = random.choice(profile['frequency_ratings'])
            
            # Set specialty risk factor
            min_risk, max_risk = profile['risk_factor_range']
            provider.specialty_risk_factor = round(random.uniform(min_risk, max_risk), 2)
            
            # Set compliance score
            min_compliance, max_compliance = profile['compliance_score_range']
            provider.compliance_score = round(random.uniform(min_compliance, max_compliance), 2)
        
        logger.info(f"Generated billing attributes for {len(providers)} providers")
        return providers
    
    def update_provider_billing_attributes(self, providers: List[Provider], simulation_date: date = None) -> int:
        """
        Update provider billing attributes in the database.
        
        Args:
            providers: List of providers with billing attributes to update
            simulation_date: The simulation date
            
        Returns:
            Number of providers updated
        """
        if not providers:
            return 0
            
        if simulation_date is None:
            simulation_date = date.today()
        
        updated_count = 0
        
        for provider in providers:
            provider_id = getattr(provider, 'provider_id', 0)
            if provider_id == 0:
                continue
                
            try:
                query = """
                UPDATE Insurance.Providers
                SET BillingPatternScore = ?, AvgClaimValue = ?, ClaimFrequencyRating = ?,
                    SpecialtyRiskFactor = ?, ComplianceScore = ?, LastModified = ?
                WHERE ProviderID = ?
                """
                execute_non_query(query, (
                    provider.billing_pattern_score,
                    provider.avg_claim_value,
                    provider.claim_frequency_rating,
                    provider.specialty_risk_factor,
                    provider.compliance_score,
                    simulation_date,
                    provider_id
                ), simulation_date)
                
                updated_count += 1
            except Exception as e:
                logger.error(f"Error updating provider {provider_id} billing attributes: {e}")
        
        logger.info(f"Updated billing attributes for {updated_count} providers in database")
        return updated_count
    
    def analyze_provider_claim_patterns(self, provider_id: int, simulation_date: date = None) -> Dict[str, Any]:
        """
        Analyze claim patterns for a specific provider.
        
        Args:
            provider_id: The provider ID to analyze
            simulation_date: The simulation date
            
        Returns:
            A dictionary with analysis results
        """
        if simulation_date is None:
            simulation_date = date.today()
            
        # Get claims for this provider in the last 12 months
        start_date = simulation_date - timedelta(days=365)
        
        try:
            claims_data = execute_query("""
                SELECT 
                    ClaimType, 
                    ServiceDescription,
                    ChargedAmount, 
                    MedicareAmount,
                    InsuranceAmount,
                    COUNT(*) as ClaimCount,
                    AVG(ChargedAmount) as AvgChargedAmount,
                    MAX(ChargedAmount) as MaxChargedAmount,
                    MIN(ChargedAmount) as MinChargedAmount
                FROM Insurance.Claims
                WHERE ProviderID = ? AND ServiceDate BETWEEN ? AND ?
                GROUP BY ClaimType, ServiceDescription, ChargedAmount, MedicareAmount, InsuranceAmount
                ORDER BY ClaimCount DESC
            """, (provider_id, start_date, simulation_date))
            
            # Analyze the results
            total_claims = sum(claim['ClaimCount'] for claim in claims_data) if claims_data else 0
            unique_services = len(claims_data) if claims_data else 0
            avg_charged = sum(claim['AvgChargedAmount'] * claim['ClaimCount'] for claim in claims_data) / total_claims if total_claims > 0 else 0
            
            # Identify potential patterns
            patterns = []
            if claims_data:
                # Look for frequently repeated exact amounts
                for claim in claims_data:
                    if claim['ClaimCount'] > 5:
                        patterns.append({
                            'type': 'Repeated Exact Amount',
                            'description': f"Same amount ({claim['ChargedAmount']}) charged {claim['ClaimCount']} times for {claim['ServiceDescription']}",
                            'frequency': claim['ClaimCount'],
                            'confidence': min(0.5 + (claim['ClaimCount'] / 20), 0.95)
                        })
                
                # Look for round number billing
                round_numbers = [claim for claim in claims_data if claim['ChargedAmount'] % 10 == 0]
                if round_numbers:
                    round_number_count = sum(claim['ClaimCount'] for claim in round_numbers)
                    round_number_percentage = round_number_count / total_claims if total_claims > 0 else 0
                    if round_number_percentage > 0.7:  # If more than 70% are round numbers
                        patterns.append({
                            'type': 'Round Number Billing',
                            'description': f"{round_number_percentage:.1%} of claims are round numbers",
                            'frequency': round_number_count,
                            'confidence': round_number_percentage
                        })
            
            return {
                'provider_id': provider_id,
                'total_claims': total_claims,
                'unique_services': unique_services,
                'avg_charged_amount': avg_charged,
                'analysis_date': simulation_date,
                'patterns': patterns
            }
        except Exception as e:
            logger.error(f"Error analyzing provider {provider_id} claim patterns: {e}")
            return {
                'provider_id': provider_id,
                'error': str(e),
                'analysis_date': simulation_date
            }