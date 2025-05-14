"""
Coverage plan generator for the Health Insurance AU simulation.
"""
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from health_insurance_au.config import HOSPITAL_TIERS, DEFAULT_WAITING_PERIODS
from health_insurance_au.models.models import CoveragePlan
from health_insurance_au.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

# Define some sample plan names and details based on Bupa
HOSPITAL_PLANS = [
    {
        'name': 'Basic Hospital',
        'tier': 'Basic',
        'base_premium': 90.0,
    },
    {
        'name': 'Bronze Hospital',
        'tier': 'Bronze',
        'base_premium': 120.0,
    },
    {
        'name': 'Bronze Plus Hospital',
        'tier': 'Bronze',
        'base_premium': 140.0,
    },
    {
        'name': 'Silver Hospital',
        'tier': 'Silver',
        'base_premium': 160.0,
    },
    {
        'name': 'Silver Plus Hospital',
        'tier': 'Silver',
        'base_premium': 180.0,
    },
    {
        'name': 'Gold Hospital',
        'tier': 'Gold',
        'base_premium': 220.0,
    }
]

EXTRAS_PLANS = [
    {
        'name': 'Basic Extras',
        'base_premium': 30.0,
        'coverage': {
            'dental': {'annual_limit': 500, 'preventative': '60%', 'general': '50%'},
            'optical': {'annual_limit': 200},
            'physio': {'annual_limit': 300, 'per_visit': '$40'}
        }
    },
    {
        'name': 'Mid Extras',
        'base_premium': 45.0,
        'coverage': {
            'dental': {'annual_limit': 800, 'preventative': '70%', 'general': '60%'},
            'optical': {'annual_limit': 300},
            'physio': {'annual_limit': 450, 'per_visit': '$50'},
            'chiro': {'annual_limit': 350, 'per_visit': '$40'},
            'remedial_massage': {'annual_limit': 300, 'per_visit': '$35'}
        }
    },
    {
        'name': 'Top Extras',
        'base_premium': 65.0,
        'coverage': {
            'dental': {'annual_limit': 1200, 'preventative': '80%', 'general': '70%', 'major': '60%'},
            'optical': {'annual_limit': 400},
            'physio': {'annual_limit': 700, 'per_visit': '$60'},
            'chiro': {'annual_limit': 500, 'per_visit': '$50'},
            'podiatry': {'annual_limit': 400, 'per_visit': '$45'},
            'psychology': {'annual_limit': 500, 'per_visit': '$80'},
            'remedial_massage': {'annual_limit': 400, 'per_visit': '$45'},
            'acupuncture': {'annual_limit': 300, 'per_visit': '$40'}
        }
    }
]

COMBINED_PLANS = [
    {
        'name': 'Basic Bundle',
        'hospital_tier': 'Basic',
        'base_premium': 110.0,
        'hospital_component': 'Basic Hospital',
        'extras_component': 'Basic Extras'
    },
    {
        'name': 'Bronze Bundle',
        'hospital_tier': 'Bronze',
        'base_premium': 150.0,
        'hospital_component': 'Bronze Hospital',
        'extras_component': 'Mid Extras'
    },
    {
        'name': 'Silver Bundle',
        'hospital_tier': 'Silver',
        'base_premium': 200.0,
        'hospital_component': 'Silver Hospital',
        'extras_component': 'Mid Extras'
    },
    {
        'name': 'Gold Bundle',
        'hospital_tier': 'Gold',
        'base_premium': 270.0,
        'hospital_component': 'Gold Hospital',
        'extras_component': 'Top Extras'
    }
]

def generate_coverage_plans(count: int = 5) -> List[CoveragePlan]:
    """
    Generate a list of coverage plans.
    
    Args:
        count: Number of plans to generate
        
    Returns:
        A list of CoveragePlan objects
    """
    plans = []
    
    # Determine how many of each type to create
    hospital_count = max(1, count // 3)
    extras_count = max(1, count // 3)
    combined_count = max(1, count - hospital_count - extras_count)
    
    # Generate hospital plans
    for i in range(hospital_count):
        template = random.choice(HOSPITAL_PLANS)
        
        # Add some variation to the premium
        variation = random.uniform(0.9, 1.1)
        monthly_premium = round(template['base_premium'] * variation, 2)
        
        # Generate excess options
        if template['tier'] in ['Basic', 'Bronze']:
            excess_options = [500, 750]
        else:
            excess_options = [0, 250, 500, 750]
        
        # Generate waiting periods
        waiting_periods = DEFAULT_WAITING_PERIODS.copy()
        
        # Generate coverage details
        coverage_details = {
            'description': f"{template['name']} provides cover for {template['tier']} tier hospital services",
            'included_services': [],
            'restricted_services': [],
            'excluded_services': []
        }
        
        # Add services based on tier
        if template['tier'] == 'Basic':
            coverage_details['included_services'] = ['Accidents', 'Ambulance']
            coverage_details['restricted_services'] = ['Rehabilitation', 'Psychiatric services']
            coverage_details['excluded_services'] = ['Heart and vascular system', 'Joint replacements', 'Pregnancy and birth']
        elif template['tier'] == 'Bronze':
            coverage_details['included_services'] = ['Accidents', 'Ambulance', 'Dental surgery', 'Hernia and appendix']
            coverage_details['restricted_services'] = ['Rehabilitation', 'Psychiatric services']
            coverage_details['excluded_services'] = ['Heart and vascular system', 'Joint replacements', 'Pregnancy and birth']
        elif template['tier'] == 'Silver':
            coverage_details['included_services'] = ['Accidents', 'Ambulance', 'Dental surgery', 'Hernia and appendix', 'Heart and vascular system', 'Lung and chest']
            coverage_details['restricted_services'] = ['Rehabilitation', 'Psychiatric services', 'Pregnancy and birth']
            coverage_details['excluded_services'] = ['Joint replacements']
        else:  # Gold
            coverage_details['included_services'] = ['Accidents', 'Ambulance', 'Dental surgery', 'Hernia and appendix', 'Heart and vascular system', 'Lung and chest', 'Joint replacements', 'Pregnancy and birth', 'Rehabilitation', 'Psychiatric services']
            coverage_details['restricted_services'] = []
            coverage_details['excluded_services'] = []
        
        # Create the plan
        plan = CoveragePlan(
            plan_code=f"H{i+1:03d}",
            plan_name=template['name'],
            plan_type='Hospital',
            hospital_tier=template['tier'],
            monthly_premium=monthly_premium,
            annual_premium=monthly_premium * 12,
            excess_options=excess_options,
            waiting_periods=waiting_periods,
            coverage_details=coverage_details,
            effective_date=date.today() - timedelta(days=random.randint(30, 365))
        )
        
        plans.append(plan)
    
    # Generate extras plans
    for i in range(extras_count):
        template = random.choice(EXTRAS_PLANS)
        
        # Add some variation to the premium
        variation = random.uniform(0.9, 1.1)
        monthly_premium = round(template['base_premium'] * variation, 2)
        
        # Generate waiting periods (simpler for extras)
        waiting_periods = {
            'general': 2,
            'major_dental': 12,
            'optical': 2
        }
        
        # Create the plan
        plan = CoveragePlan(
            plan_code=f"E{i+1:03d}",
            plan_name=template['name'],
            plan_type='Extras',
            monthly_premium=monthly_premium,
            annual_premium=monthly_premium * 12,
            waiting_periods=waiting_periods,
            coverage_details=template['coverage'],
            effective_date=date.today() - timedelta(days=random.randint(30, 365))
        )
        
        plans.append(plan)
    
    # Generate combined plans
    for i in range(combined_count):
        template = random.choice(COMBINED_PLANS)
        
        # Add some variation to the premium
        variation = random.uniform(0.9, 1.1)
        monthly_premium = round(template['base_premium'] * variation, 2)
        
        # Generate excess options
        if template['hospital_tier'] in ['Basic', 'Bronze']:
            excess_options = [500, 750]
        else:
            excess_options = [0, 250, 500, 750]
        
        # Generate waiting periods (combined from both)
        waiting_periods = DEFAULT_WAITING_PERIODS.copy()
        waiting_periods.update({
            'major_dental': 12,
            'optical': 2
        })
        
        # Create the plan
        plan = CoveragePlan(
            plan_code=f"C{i+1:03d}",
            plan_name=template['name'],
            plan_type='Combined',
            hospital_tier=template['hospital_tier'],
            monthly_premium=monthly_premium,
            annual_premium=monthly_premium * 12,
            excess_options=excess_options,
            waiting_periods=waiting_periods,
            coverage_details={
                'hospital_component': template['hospital_component'],
                'extras_component': template['extras_component']
            },
            effective_date=date.today() - timedelta(days=random.randint(30, 365))
        )
        
        plans.append(plan)
    
    logger.info(f"Generated {len(plans)} coverage plans")
    return plans