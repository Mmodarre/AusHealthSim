#!/usr/bin/env python3
"""
Utility script to manage the used members list.
"""

import argparse
import logging
import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from health_insurance_au.utils.member_tracker import load_used_members, reset_used_members
from health_insurance_au.utils.logging_config import configure_logging, get_logger

# Set up logging
configure_logging()
logger = get_logger(__name__)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Manage the used members list')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show the list of used member IDs')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset the list of used member IDs')
    
    args = parser.parse_args()
    
    if args.command == 'show':
        # Show the list of used member IDs
        used_members = load_used_members()
        print(f"Used member IDs ({len(used_members)}):")
        for member_id in sorted(used_members):
            print(f"  {member_id}")
    elif args.command == 'reset':
        # Reset the list of used member IDs
        reset_used_members()
        print("Reset the list of used member IDs")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()