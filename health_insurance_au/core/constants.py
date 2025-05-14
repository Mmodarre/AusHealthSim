"""
Constants specific to the Australian health insurance system.
"""

# Hospital Cover Tiers
HOSPITAL_TIER_BASIC = "Basic"
HOSPITAL_TIER_BRONZE = "Bronze"
HOSPITAL_TIER_SILVER = "Silver"
HOSPITAL_TIER_GOLD = "Gold"

# Waiting Periods (in months)
WAITING_PERIOD_GENERAL = 2
WAITING_PERIOD_PRE_EXISTING = 12
WAITING_PERIOD_PREGNANCY = 12

# Australian States and Territories
STATES = {
    "ACT": "Australian Capital Territory",
    "NSW": "New South Wales",
    "NT": "Northern Territory",
    "QLD": "Queensland",
    "SA": "South Australia",
    "TAS": "Tasmania",
    "VIC": "Victoria",
    "WA": "Western Australia"
}

# Private Health Insurance Rebate Tiers
PHI_REBATE_TIERS = {
    "Base": {
        "single_income_threshold": 90000,
        "family_income_threshold": 180000,
        "rebate_under_65": 0.25,
        "rebate_65_69": 0.29,
        "rebate_70_plus": 0.33
    },
    "Tier1": {
        "single_income_threshold": 105000,
        "family_income_threshold": 210000,
        "rebate_under_65": 0.17,
        "rebate_65_69": 0.21,
        "rebate_70_plus": 0.25
    },
    "Tier2": {
        "single_income_threshold": 140000,
        "family_income_threshold": 280000,
        "rebate_under_65": 0.08,
        "rebate_65_69": 0.12,
        "rebate_70_plus": 0.16
    },
    "Tier3": {
        "single_income_threshold": float('inf'),
        "family_income_threshold": float('inf'),
        "rebate_under_65": 0.0,
        "rebate_65_69": 0.0,
        "rebate_70_plus": 0.0
    }
}

# Lifetime Health Cover (LHC) Loading
LHC_BASE_AGE = 31
LHC_LOADING_RATE = 0.02  # 2% per year
LHC_LOADING_MAX = 0.70   # 70% maximum loading