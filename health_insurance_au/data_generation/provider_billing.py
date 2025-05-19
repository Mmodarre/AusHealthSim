"""
Provider billing pattern generator for enhanced simulation.
"""
from datetime import date, datetime, timedelta
import random
from typing import Dict, List, Any, Optional

from health_insurance_au.utils.db_utils import execute_query, execute_non_query, bulk_insert
from health_insurance_au.models.models import Provider

class ProviderBillingGenerator:
    """Generator for provider billing patterns."""
    
    def __init__(self):
        """Initialize the provider billing generator."""
        pass
    
    def generate_billing_attributes(self, simulation_date: date) -> Dict[str, int]:
        """
        Generate billing pattern attributes for providers.
        
        Args:
            simulation_date: The simulation date
            
        Returns:
            Dictionary with statistics about updated providers
        """
        # Get all active providers
        providers = self._get_active_providers()
        
        # Update each provider with billing pattern attributes
        updated_providers = 0
        for provider in providers:
            # Generate billing pattern attributes
            billing_pattern_score = self._generate_billing_pattern_score(provider)
            avg_claim_value = self._calculate_avg_claim_value(provider)
            claim_frequency_rating = self._calculate_claim_frequency_rating(provider)
            specialty_risk_factor = self._calculate_specialty_risk_factor(provider)
            compliance_score = self._generate_compliance_score(provider)
            
            # Update the provider in the database
            try:
                query = """
                UPDATE Insurance.Providers
                SET BillingPatternScore = ?,
                    AvgClaimValue = ?,
                    ClaimFrequencyRating = ?,
                    SpecialtyRiskFactor = ?,
                    ComplianceScore = ?,
                    LastModified = ?
                WHERE ProviderID = ?
                """
                execute_non_query(query, (
                    billing_pattern_score,
                    avg_claim_value,
                    claim_frequency_rating,
                    specialty_risk_factor,
                    compliance_score,
                    simulation_date,
                    provider['ProviderID']
                ))
                updated_providers += 1
            except Exception as e:
                print(f"Error updating provider {provider['ProviderID']}: {e}")
        
        return {
            'providers_updated': updated_providers
        }
    
    def _get_active_providers(self) -> List[Dict[str, Any]]:
        """Get all active providers from the database."""
        try:
            query = """
            SELECT p.*, 
                (SELECT COUNT(*) FROM Insurance.Claims c WHERE c.ProviderID = p.ProviderID) AS ClaimCount,
                (SELECT AVG(c.ChargedAmount) FROM Insurance.Claims c WHERE c.ProviderID = p.ProviderID) AS AvgAmount
            FROM Insurance.Providers p
            WHERE p.IsActive = 1
            """
            return execute_query(query)
        except Exception as e:
            print(f"Error getting active providers: {e}")
            return []
    
    def _generate_billing_pattern_score(self, provider: Dict[str, Any]) -> float:
        """
        Generate a billing pattern score for a provider.
        
        The score is based on:
        - Provider type
        - Claim count
        - Average claim amount
        - Random variation
        
        Returns:
            A score between 0.0 and 1.0
        """
        # Base score
        base_score = 0.5
        
        # Adjust based on provider type
        provider_type = provider['ProviderType']
        if provider_type == 'Hospital':
            base_score += 0.1
        elif provider_type == 'Specialist':
            base_score += 0.05
        
        # Adjust based on claim count
        claim_count = provider.get('ClaimCount', 0)
        if claim_count > 100:
            base_score += 0.1
        elif claim_count > 50:
            base_score += 0.05
        
        # Adjust based on average claim amount
        avg_amount = provider.get('AvgAmount', 0)
        # Handle None value for avg_amount
        if avg_amount is not None:
            if avg_amount > 1000:
                base_score += 0.1
            elif avg_amount > 500:
                base_score += 0.05
        
        # Add random variation
        base_score += random.uniform(-0.1, 0.1)
        
        # Ensure the score is between 0.0 and 1.0
        return max(0.0, min(1.0, base_score))
    
    def _calculate_avg_claim_value(self, provider: Dict[str, Any]) -> float:
        """Calculate the average claim value for a provider."""
        avg_amount = provider.get('AvgAmount', 0)
        if avg_amount is None:
            # If no claims, generate a random amount based on provider type
            provider_type = provider['ProviderType']
            if provider_type == 'Hospital':
                avg_amount = random.uniform(800, 2000)
            elif provider_type == 'Specialist':
                avg_amount = random.uniform(200, 800)
            else:
                avg_amount = random.uniform(100, 500)
        
        return round(float(avg_amount), 2)
    
    def _calculate_claim_frequency_rating(self, provider: Dict[str, Any]) -> str:
        """Calculate the claim frequency rating for a provider."""
        claim_count = provider.get('ClaimCount', 0)
        
        if claim_count > 100:
            return 'Very High'
        elif claim_count > 50:
            return 'High'
        elif claim_count > 20:
            return 'Medium'
        elif claim_count > 5:
            return 'Low'
        else:
            return 'Very Low'
    
    def _calculate_specialty_risk_factor(self, provider: Dict[str, Any]) -> float:
        """Calculate the specialty risk factor for a provider."""
        provider_type = provider['ProviderType']
        
        # Base risk factor
        base_factor = 1.0
        
        # Adjust based on provider type
        if provider_type == 'Hospital':
            base_factor = 1.2
        elif provider_type == 'Specialist':
            base_factor = 1.1
        elif provider_type == 'General Practitioner':
            base_factor = 0.9
        
        # Add random variation
        base_factor += random.uniform(-0.2, 0.2)
        
        # Ensure the factor is positive
        return max(0.1, base_factor)
    
    def _generate_compliance_score(self, provider: Dict[str, Any]) -> float:
        """
        Generate a compliance score for a provider.
        
        Returns:
            A score between 0.0 and 1.0
        """
        # Base score
        base_score = 0.8
        
        # Add random variation
        base_score += random.uniform(-0.2, 0.2)
        
        # Ensure the score is between 0.0 and 1.0
        return max(0.0, min(1.0, base_score))