"""
Configuration settings for the Health Insurance AU simulation.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

from health_insurance_au.utils.logging_config import get_logger
from health_insurance_au.utils.env_utils import get_db_config

# Set up logging
logger = get_logger(__name__)

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Path to environment file
DEFAULT_ENV_FILE = os.path.join(PROJECT_ROOT, 'config', 'db_config.env')

# Logging configuration
LOG_CONFIG = {
    'default_level': 'INFO',  # Default log level if not specified
    'log_dir': os.path.join(PROJECT_ROOT, 'logs'),
    'log_file': 'health_insurance_au.log',  # Default log file name
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Paths
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
SAMPLE_DATA_PATH = os.path.join(DATA_DIR, 'health_insurance_demo_10k.json')

# Simulation defaults
DEFAULT_START_DATE = datetime(2023, 1, 1)
DEFAULT_END_DATE = datetime.now()
DEFAULT_SIMULATION_DAYS = (DEFAULT_END_DATE - DEFAULT_START_DATE).days

# Australian states and territories
STATES = {
    'NSW': 'New South Wales',
    'VIC': 'Victoria',
    'QLD': 'Queensland',
    'WA': 'Western Australia',
    'SA': 'South Australia',
    'TAS': 'Tasmania',
    'ACT': 'Australian Capital Territory',
    'NT': 'Northern Territory'
}

# Hospital tiers as per Australian PHI reforms
HOSPITAL_TIERS = ['Basic', 'Bronze', 'Silver', 'Gold']

# Default waiting periods (in months)
DEFAULT_WAITING_PERIODS = {
    'general': 2,
    'pre_existing': 12,
    'pregnancy': 12,
    'psychiatric': 2,
    'rehabilitation': 2
}

# PHI Rebate tiers for 2023-2024
PHI_REBATE_TIERS = [
    {
        'name': 'Base',
        'income_single': 93000,
        'income_family': 186000,
        'rebate_under65': 24.608,
        'rebate_65to69': 28.710,
        'rebate_70plus': 32.812
    },
    {
        'name': 'Tier1',
        'income_single': 108000,
        'income_family': 216000,
        'rebate_under65': 16.405,
        'rebate_65to69': 20.507,
        'rebate_70plus': 24.608
    },
    {
        'name': 'Tier2',
        'income_single': 144000,
        'income_family': 288000,
        'rebate_under65': 8.202,
        'rebate_65to69': 12.303,
        'rebate_70plus': 16.405
    },
    {
        'name': 'Tier3',
        'income_single': 144001,  # Above this threshold
        'income_family': 288001,  # Above this threshold
        'rebate_under65': 0,
        'rebate_65to69': 0,
        'rebate_70plus': 0
    }
]

# Claim types
CLAIM_TYPES = [
    'Hospital',
    'Medical',
    'Dental',
    'Optical',
    'Physiotherapy',
    'Chiropractic',
    'Psychology',
    'Podiatry',
    'Acupuncture',
    'Naturopathy',
    'Remedial Massage',
    'Ambulance'
]

# Load the database configuration
DB_CONFIG = get_db_config(DEFAULT_ENV_FILE)