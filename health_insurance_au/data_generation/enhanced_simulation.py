"""
Integration module for enhanced simulation capabilities.
"""
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from health_insurance_au.data_generation.simulation_orchestrator import SimulationOrchestrator
from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

def run_enhanced_simulation(simulation_date: date = None, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run an enhanced simulation with fraud patterns, financial transactions, and actuarial data.
    
    Args:
        simulation_date: The date to simulate
        config: Configuration dictionary with simulation parameters
        
    Returns:
        A dictionary with simulation results
    """
    if simulation_date is None:
        simulation_date = date.today()
    
    orchestrator = SimulationOrchestrator()
    results = orchestrator.run_enhanced_simulation(simulation_date, config)
    
    logger.info(f"Enhanced simulation completed for {simulation_date}")
    return results

def run_historical_enhanced_simulation(
    start_date: date,
    end_date: date = None,
    frequency: str = 'monthly',
    config: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Run a historical enhanced simulation over a date range.
    
    Args:
        start_date: The start date for the simulation
        end_date: The end date for the simulation (default: today)
        frequency: The frequency of simulation runs ('daily', 'weekly', 'monthly')
        config: Configuration dictionary with simulation parameters
        
    Returns:
        A list of dictionaries with simulation results
    """
    if end_date is None:
        end_date = date.today()
        
    logger.info(f"Running historical enhanced simulation from {start_date} to {end_date} with {frequency} frequency...")
    
    # Determine the date increment based on frequency
    if frequency == 'daily':
        date_increment = timedelta(days=1)
    elif frequency == 'weekly':
        date_increment = timedelta(days=7)
    elif frequency == 'monthly':
        # Start at first of the month
        current_date = date(start_date.year, start_date.month, 1)
        
        # Function to increment by one month
        def increment_month(d):
            if d.month == 12:
                return date(d.year + 1, 1, 1)
            else:
                return date(d.year, d.month + 1, 1)
        
        date_increment = None  # We'll handle monthly increments differently
    else:
        logger.error(f"Invalid frequency: {frequency}")
        return []
    
    results = []
    
    # Run the simulation for each date
    current_date = start_date
    while current_date <= end_date:
        # Vary the configuration slightly for each run
        run_config = config.copy() if config else {}
        
        # Add some randomness to the configuration
        if 'actuarial_metrics_count' in run_config:
            run_config['actuarial_metrics_count'] = max(10, run_config['actuarial_metrics_count'] + random.randint(-10, 10))
        
        if 'claim_pattern_count' in run_config:
            run_config['claim_pattern_count'] = max(5, run_config['claim_pattern_count'] + random.randint(-5, 5))
        
        if 'financial_transaction_count' in run_config:
            run_config['financial_transaction_count'] = max(10, run_config['financial_transaction_count'] + random.randint(-10, 10))
        
        # Run the simulation
        result = run_enhanced_simulation(current_date, run_config)
        results.append(result)
        
        # Increment the date
        if frequency == 'monthly':
            current_date = increment_month(current_date)
        else:
            current_date += date_increment
    
    logger.info(f"Historical enhanced simulation completed with {len(results)} runs")
    return results