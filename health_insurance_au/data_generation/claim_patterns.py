"""
Claim pattern generator for enhanced simulation.
"""
from datetime import date, datetime, timedelta
import random
from typing import Dict, List, Any, Optional

from health_insurance_au.utils.db_utils import execute_query, execute_non_query, bulk_insert
from health_insurance_au.models.models import ClaimPattern

class ClaimPatternGenerator:
    """Generator for claim patterns."""
    
    def __init__(self):
        """Initialize the claim pattern generator."""
        pass
    
    def generate_patterns(self, simulation_date: date) -> Dict[str, int]:
        """
        Generate claim patterns.
        
        Args:
            simulation_date: The simulation date
            
        Returns:
            Dictionary with statistics about generated patterns
        """
        # Get members with claims
        members = self._get_members_with_claims(simulation_date)
        
        # Get providers with claims
        providers = self._get_providers_with_claims(simulation_date)
        
        # Get claims for analysis
        claims = self._get_claims_for_analysis(simulation_date)
        
        # Get existing patterns to avoid duplicates
        existing_patterns = self._get_existing_patterns()
        
        # Analyze claims and generate patterns
        patterns = []
        
        # Group claims by member and provider
        member_provider_claims = {}
        for claim in claims:
            key = (claim['MemberID'], claim['ProviderID'])
            if key not in member_provider_claims:
                member_provider_claims[key] = []
            member_provider_claims[key].append(claim)
        
        # Analyze each member-provider combination
        for (member_id, provider_id), member_claims in member_provider_claims.items():
            # Only generate patterns for combinations with multiple claims
            if len(member_claims) < 2:
                continue
            
            # Check for high frequency pattern
            if len(member_claims) >= 5:
                # Check if this pattern already exists
                pattern_key = (member_id, provider_id, "High Frequency")
                if pattern_key not in existing_patterns:
                    pattern = self._create_high_frequency_pattern(member_id, provider_id, member_claims, simulation_date)
                    patterns.append(pattern)
            
            # Check for high value pattern
            avg_amount = float(sum(claim['ChargedAmount'] for claim in member_claims)) / len(member_claims)
            if avg_amount > 1000:
                # Check if this pattern already exists
                pattern_key = (member_id, provider_id, "High Value")
                if pattern_key not in existing_patterns:
                    pattern = self._create_high_value_pattern(member_id, provider_id, member_claims, simulation_date)
                    patterns.append(pattern)
            
            # Check for service clustering pattern
            service_dates = [claim['ServiceDate'] for claim in member_claims]
            date_diffs = []
            for i in range(1, len(service_dates)):
                diff = (service_dates[i] - service_dates[i-1]).days
                date_diffs.append(diff)
            
            if len(date_diffs) > 0 and sum(date_diffs) / len(date_diffs) < 7:
                # Check if this pattern already exists
                pattern_key = (member_id, provider_id, "Service Clustering")
                if pattern_key not in existing_patterns:
                    pattern = self._create_service_clustering_pattern(member_id, provider_id, member_claims, simulation_date)
                    patterns.append(pattern)
        
        # Insert patterns into the database
        patterns_inserted = 0
        if patterns:
            pattern_dicts = [p.to_dict() for p in patterns]
            patterns_inserted = bulk_insert("Insurance.ClaimPatterns", pattern_dicts)
        
        return {
            'patterns_generated': patterns_inserted
        }
    
    def _get_existing_patterns(self) -> set:
        """Get existing patterns from the database to avoid duplicates."""
        try:
            query = """
            SELECT MemberID, ProviderID, PatternType
            FROM Insurance.ClaimPatterns
            """
            results = execute_query(query)
            
            # Create a set of tuples (MemberID, ProviderID, PatternType) for quick lookup
            return {(row['MemberID'], row['ProviderID'], row['PatternType']) for row in results}
        except Exception as e:
            print(f"Error getting existing patterns: {e}")
            return set()
    
    def _get_members_with_claims(self, simulation_date: date) -> List[Dict[str, Any]]:
        """Get members with claims from the database."""
        try:
            # Get members with claims in the last 90 days
            start_date = simulation_date - timedelta(days=90)
            query = """
            SELECT DISTINCT m.*
            FROM Insurance.Members m
            JOIN Insurance.Claims c ON m.MemberID = c.MemberID
            WHERE c.ServiceDate BETWEEN ? AND ?
            """
            return execute_query(query, (start_date, simulation_date))
        except Exception as e:
            print(f"Error getting members with claims: {e}")
            return []
    
    def _get_providers_with_claims(self, simulation_date: date) -> List[Dict[str, Any]]:
        """Get providers with claims from the database."""
        try:
            # Get providers with claims in the last 90 days
            start_date = simulation_date - timedelta(days=90)
            query = """
            SELECT DISTINCT p.*
            FROM Insurance.Providers p
            JOIN Insurance.Claims c ON p.ProviderID = c.ProviderID
            WHERE c.ServiceDate BETWEEN ? AND ?
            """
            return execute_query(query, (start_date, simulation_date))
        except Exception as e:
            print(f"Error getting providers with claims: {e}")
            return []
    
    def _get_claims_for_analysis(self, simulation_date: date) -> List[Dict[str, Any]]:
        """Get claims for analysis from the database."""
        try:
            # Get claims from the last 90 days
            start_date = simulation_date - timedelta(days=90)
            query = """
            SELECT c.*
            FROM Insurance.Claims c
            WHERE c.ServiceDate BETWEEN ? AND ?
            """
            return execute_query(query, (start_date, simulation_date))
        except Exception as e:
            print(f"Error getting claims for analysis: {e}")
            return []
    
    def _create_high_frequency_pattern(self, member_id: int, provider_id: int, claims: List[Dict[str, Any]], simulation_date: date) -> ClaimPattern:
        """Create a high frequency claim pattern."""
        service_dates = [claim['ServiceDate'] for claim in claims]
        first_date = min(service_dates)
        last_date = max(service_dates)
        
        return ClaimPattern(
            member_id=member_id,
            provider_id=provider_id,
            pattern_type="High Frequency",
            pattern_description=f"High frequency of claims ({len(claims)} claims in {(last_date - first_date).days} days)",
            first_detected_date=first_date,
            last_detected_date=last_date,
            occurrence_count=len(claims),
            average_amount=float(sum(claim['ChargedAmount'] for claim in claims)) / len(claims),
            confidence_score=min(0.9, 0.5 + 0.05 * len(claims)),
            status="Active"
        )
    
    def _create_high_value_pattern(self, member_id: int, provider_id: int, claims: List[Dict[str, Any]], simulation_date: date) -> ClaimPattern:
        """Create a high value claim pattern."""
        service_dates = [claim['ServiceDate'] for claim in claims]
        first_date = min(service_dates)
        last_date = max(service_dates)
        avg_amount = float(sum(claim['ChargedAmount'] for claim in claims)) / len(claims)
        
        return ClaimPattern(
            member_id=member_id,
            provider_id=provider_id,
            pattern_type="High Value",
            pattern_description=f"High average claim value (${avg_amount:.2f} across {len(claims)} claims)",
            first_detected_date=first_date,
            last_detected_date=last_date,
            occurrence_count=len(claims),
            average_amount=avg_amount,
            confidence_score=min(0.9, 0.5 + 0.0001 * float(avg_amount)),
            status="Active"
        )
    
    def _create_service_clustering_pattern(self, member_id: int, provider_id: int, claims: List[Dict[str, Any]], simulation_date: date) -> ClaimPattern:
        """Create a service clustering claim pattern."""
        service_dates = [claim['ServiceDate'] for claim in claims]
        first_date = min(service_dates)
        last_date = max(service_dates)
        
        return ClaimPattern(
            member_id=member_id,
            provider_id=provider_id,
            pattern_type="Service Clustering",
            pattern_description=f"Services clustered closely together ({len(claims)} claims in {(last_date - first_date).days} days)",
            first_detected_date=first_date,
            last_detected_date=last_date,
            occurrence_count=len(claims),
            average_amount=float(sum(claim['ChargedAmount'] for claim in claims)) / len(claims),
            confidence_score=min(0.9, 0.5 + 0.1 * (1 / (float((last_date - first_date).days) / len(claims) + 1))),
            status="Active"
        )