#!/usr/bin/env python3
"""
Run a historical simulation with enhanced features enabled.
"""
import argparse
from datetime import datetime
from health_insurance_au.simulation.simulation import HealthInsuranceSimulation
from health_insurance_au.utils.logging_config import configure_logging, get_logger

# Set up logging
configure_logging()
logger = get_logger(__name__)

def parse_date(date_str):
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Run a historical simulation with enhanced features')
    parser.add_argument('--start-date', type=parse_date, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=parse_date, required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--frequency', choices=['daily', 'weekly', 'monthly'], default='daily', help='Simulation frequency')
    parser.add_argument('--use-dynamic-data', action='store_true', help='Use dynamically generated data')
    
    args = parser.parse_args()
    
    # Initialize simulation
    simulation = HealthInsuranceSimulation()
    
    # Run historical simulation with enhanced features enabled
    logger.info(f"Running historical simulation from {args.start_date} to {args.end_date} with enhanced features")
    simulation.run_historical_simulation(
        start_date=args.start_date,
        end_date=args.end_date,
        frequency=args.frequency,
        use_dynamic_data=args.use_dynamic_data,
        run_enhanced=True  # Enable enhanced features
    )
    logger.info("Historical simulation completed")

if __name__ == '__main__':
    main()