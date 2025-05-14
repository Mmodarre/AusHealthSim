"""
Environment variable utilities for the Health Insurance AU simulation.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def load_env_file(env_file_path: str) -> Dict[str, str]:
    """
    Load environment variables from a file.
    
    Args:
        env_file_path: Path to the environment file
        
    Returns:
        A dictionary of environment variables
    """
    env_vars = {}
    
    try:
        env_path = Path(env_file_path)
        if not env_path.exists():
            logger.warning(f"Environment file not found: {env_file_path}")
            return env_vars
            
        with open(env_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
                
        logger.info(f"Loaded {len(env_vars)} environment variables from {env_file_path}")
        return env_vars
        
    except Exception as e:
        logger.error(f"Error loading environment file {env_file_path}: {e}")
        return {}

def get_db_config(env_file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get database configuration from environment variables or file.
    
    Args:
        env_file_path: Optional path to the environment file
        
    Returns:
        A dictionary with database configuration
    """
    # Default configuration
    db_config = {
        'server': os.environ.get('DB_SERVER', ''),
        'database': os.environ.get('DB_DATABASE', 'HealthInsuranceAU'),
        'username': os.environ.get('DB_USERNAME', ''),
        'password': os.environ.get('DB_PASSWORD', ''),
        'driver': os.environ.get('DB_DRIVER', '{ODBC Driver 17 for SQL Server}')
    }
    
    # Try to load from environment file if provided
    if env_file_path:
        env_vars = load_env_file(env_file_path)
        if env_vars:
            db_config['server'] = env_vars.get('DB_SERVER', db_config['server'])
            db_config['database'] = env_vars.get('DB_DATABASE', db_config['database'])
            db_config['username'] = env_vars.get('DB_USERNAME', db_config['username'])
            db_config['password'] = env_vars.get('DB_PASSWORD', db_config['password'])
            db_config['driver'] = env_vars.get('DB_DRIVER', db_config['driver'])
    
    # Validate configuration
    missing_keys = [key for key, value in db_config.items() if not value]
    if missing_keys:
        logger.warning(f"Missing database configuration keys: {', '.join(missing_keys)}")
    
    return db_config