"""
Enhanced simulation module for the health insurance simulation.
"""
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional

from health_insurance_au.data_generation.simulation_orchestrator import SimulationOrchestrator

def run_enhanced_simulation(simulation_date: date, config: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
    """
    Run enhanced simulation for a specific date.
    
    Args:
        simulation_date: The simulation date
        config: Configuration dictionary with feature flags (optional)
        
    Returns:
        Dictionary with statistics about the simulation
    """
    # Use default config if not provided
    if config is None:
        config = {
            'generate_member_risk_profiles': True,
            'generate_policy_risk_attributes': True,
            'generate_provider_billing_attributes': True,
            'apply_fraud_patterns': True,
            'generate_claim_patterns': True,
            'generate_financial_transactions': True,
            'generate_actuarial_metrics': True
        }
    
    # Create orchestrator and run simulation
    orchestrator = SimulationOrchestrator()
    results = orchestrator.run_enhanced_simulation(simulation_date, config)
    
    return results

def run_enhanced_historical_simulation(start_date: date, end_date: date, config: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
    """
    Run enhanced simulation for a range of dates.
    
    Args:
        start_date: The start date of the simulation
        end_date: The end date of the simulation
        config: Configuration dictionary with feature flags (optional)
        
    Returns:
        Dictionary with statistics about the simulation
    """
    # Use default config if not provided
    if config is None:
        config = {
            'generate_member_risk_profiles': True,
            'generate_policy_risk_attributes': True,
            'generate_provider_billing_attributes': True,
            'apply_fraud_patterns': True,
            'generate_claim_patterns': True,
            'generate_financial_transactions': True,
            'generate_actuarial_metrics': True
        }
    
    # Create orchestrator
    orchestrator = SimulationOrchestrator()
    
    # Initialize results
    results = {
        'start_date': start_date,
        'end_date': end_date,
        'days_simulated': 0,
        'members_updated': 0,
        'policies_updated': 0,
        'providers_updated': 0,
        'claims_updated': 0,
        'claim_patterns_generated': 0,
        'financial_transactions_generated': 0,
        'actuarial_metrics_generated': 0
    }
    
    # Run simulation for each day
    current_date = start_date
    while current_date <= end_date:
        day_results = orchestrator.run_enhanced_simulation(current_date, config)
        
        # Accumulate results
        results['days_simulated'] += 1
        results['members_updated'] += day_results.get('members_updated', 0)
        results['policies_updated'] += day_results.get('policies_updated', 0)
        results['providers_updated'] += day_results.get('providers_updated', 0)
        results['claims_updated'] += day_results.get('claims_updated', 0)
        results['claim_patterns_generated'] += day_results.get('claim_patterns_generated', 0)
        results['financial_transactions_generated'] += day_results.get('financial_transactions_generated', 0)
        results['actuarial_metrics_generated'] += day_results.get('actuarial_metrics_generated', 0)
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return results