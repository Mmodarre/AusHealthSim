#!/usr/bin/env python3
"""
Test runner script for the insurance simulation project.

This script runs all the tests for the project, including:
1. Unit tests
2. Integration tests
3. End-to-end tests

Usage:
    python run_tests.py [--e2e] [--date YYYY-MM-DD]

Options:
    --e2e           Run end-to-end tests (requires database connection)
    --date          Simulation date for end-to-end tests (default: today)
"""

import argparse
import os
import subprocess
import sys
from datetime import date

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

def parse_date(date_str):
    """Parse date string in YYYY-MM-DD format."""
    try:
        from datetime import datetime
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

def run_unit_tests():
    """Run unit tests using pytest."""
    print("Running unit tests...")
    result = subprocess.run(['pytest', 'tests/unit', '-v'], capture_output=True, text=True, cwd=project_root)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Unit tests failed with exit code {result.returncode}")
        print(result.stderr)
        return False
    return True

def run_integration_tests():
    """Run integration tests using pytest."""
    print("Running integration tests...")
    result = subprocess.run(['pytest', 'tests/integration', '-v'], capture_output=True, text=True, cwd=project_root)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Integration tests failed with exit code {result.returncode}")
        print(result.stderr)
        return False
    return True

def run_e2e_tests(simulation_date):
    """Run end-to-end tests."""
    print(f"Running end-to-end tests for date {simulation_date}...")
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_date_consistency_e2e.py')
    
    # Set PYTHONPATH environment variable to include project root
    env = os.environ.copy()
    env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
    
    result = subprocess.run(['python3', script_path, '--date', simulation_date.strftime('%Y-%m-%d')], 
                           capture_output=True, text=True, env=env)
    print(result.stdout)
    if result.returncode != 0:
        print(f"End-to-end tests failed with exit code {result.returncode}")
        print(result.stderr)
        return False
    return True

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Run tests for the insurance simulation project')
    parser.add_argument('--e2e', action='store_true', help='Run end-to-end tests')
    parser.add_argument('--date', type=parse_date, default=date.today(), help='Simulation date for end-to-end tests (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Change to the project root directory
    os.chdir(project_root)
    
    # Run unit tests
    unit_success = run_unit_tests()
    
    # Run integration tests
    integration_success = run_integration_tests()
    
    # Run end-to-end tests if requested
    e2e_success = True
    if args.e2e:
        e2e_success = run_e2e_tests(args.date)
    
    # Overall success
    success = unit_success and integration_success and e2e_success
    
    # Print summary
    print("\nTest Summary:")
    print(f"Unit Tests: {'PASS' if unit_success else 'FAIL'}")
    print(f"Integration Tests: {'PASS' if integration_success else 'FAIL'}")
    if args.e2e:
        print(f"End-to-End Tests: {'PASS' if e2e_success else 'FAIL'}")
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()