"""
Member tracking utilities for the Health Insurance AU simulation.
"""
import os
import json
import logging
from typing import List, Set, Dict, Any

from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

# File to store used member IDs
USED_MEMBERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "data", "used_members.json")

def load_used_members() -> Set[str]:
    """
    Load the set of member IDs that have already been used.
    
    Returns:
        A set of member IDs
    """
    try:
        if not os.path.exists(USED_MEMBERS_FILE):
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(USED_MEMBERS_FILE), exist_ok=True)
            return set()
            
        with open(USED_MEMBERS_FILE, 'r') as f:
            used_members = set(json.load(f))
            
        logger.info(f"Loaded {len(used_members)} used member IDs")
        return used_members
    except Exception as e:
        logger.warning(f"Error loading used members: {e}. Starting with empty set.")
        return set()

def save_used_members(used_members: Set[str]) -> None:
    """
    Save the set of used member IDs to the file.
    
    Args:
        used_members: Set of member IDs that have been used
    """
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(USED_MEMBERS_FILE), exist_ok=True)
        
        with open(USED_MEMBERS_FILE, 'w') as f:
            json.dump(list(used_members), f)
            
        logger.info(f"Saved {len(used_members)} used member IDs")
    except Exception as e:
        logger.error(f"Error saving used members: {e}")

def get_unused_members(data: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
    """
    Get a list of unused members from the data.
    
    Args:
        data: The sample data as a list of dictionaries
        count: Number of unused members to retrieve
        
    Returns:
        A list of dictionaries containing unused member data
    """
    # Load the set of used member IDs
    used_members = load_used_members()
    
    # Filter out members that have already been used
    unused_data = [item for item in data if item.get('member_id', '') not in used_members]
    
    if len(unused_data) < count:
        logger.warning(f"Only {len(unused_data)} unused members available, but {count} requested")
        
    # Select the requested number of members (or all available if less than requested)
    selected_count = min(count, len(unused_data))
    selected_members = unused_data[:selected_count]
    
    # Update the set of used member IDs
    for member in selected_members:
        used_members.add(member.get('member_id', ''))
    
    # Save the updated set of used member IDs
    save_used_members(used_members)
    
    logger.info(f"Selected {len(selected_members)} unused members")
    return selected_members

def reset_used_members() -> None:
    """
    Reset the list of used members (for testing or starting fresh).
    """
    try:
        if os.path.exists(USED_MEMBERS_FILE):
            os.remove(USED_MEMBERS_FILE)
        logger.info("Reset used members list")
    except Exception as e:
        logger.error(f"Error resetting used members: {e}")