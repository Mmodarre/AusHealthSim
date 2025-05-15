#!/usr/bin/env python3
"""
Generate realistic synthetic patient data for Synthea in fixed records JSON format.
This script creates demographically realistic patient profiles with life stages and variants.
"""

import json
import random
import argparse
import datetime
from faker import Faker
import numpy as np
from collections import defaultdict

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducibility, remove in production

# Constants
STATES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia'
}

RACES = {
    'white': 0.6,
    'black': 0.13,
    'asian': 0.06,
    'native': 0.01,
    'hispanic': 0.18,
    'other': 0.02
}

ETHNICITIES = {
    'hispanic': 0.18,
    'nonhispanic': 0.82
}

MARITAL_STATUS = {
    'S': 0.3,  # Single
    'M': 0.5,  # Married
    'D': 0.1,  # Divorced
    'W': 0.1   # Widowed
}

# Age distribution (realistic US population distribution)
AGE_DISTRIBUTION = [
    ((0, 18), 0.22),    # Children
    ((19, 25), 0.09),   # Young adults
    ((26, 35), 0.14),   # Early career
    ((36, 50), 0.19),   # Mid-career
    ((51, 65), 0.20),   # Late career
    ((66, 85), 0.14),   # Retirement
    ((86, 100), 0.02)   # Elderly
]

# Life events that might cause demographic changes
LIFE_EVENTS = {
    'address_change': 0.7,       # Probability of moving at least once
    'name_change': 0.3,          # Probability of name change (marriage, etc.)
    'marital_status_change': 0.4 # Probability of marital status change
}

def weighted_choice(choices_with_weights):
    """Select an item from a list of (choice, weight) tuples."""
    choices, weights = zip(*choices_with_weights)
    total = sum(weights)
    normalized_weights = [w/total for w in weights]
    return choices[np.random.choice(len(choices), p=normalized_weights)]

def generate_age_based_on_distribution():
    """Generate an age based on realistic US population distribution."""
    age_range = weighted_choice(AGE_DISTRIBUTION)
    return random.randint(age_range[0], age_range[1])

def generate_birthdate(age):
    """Generate a birthdate based on the given age."""
    today = datetime.date.today()
    birth_year = today.year - age
    
    # Generate random month and day
    month = random.randint(1, 12)
    max_day = 28 if month == 2 else 30 if month in [4, 6, 9, 11] else 31
    day = random.randint(1, max_day)
    
    # Adjust if the birthday hasn't occurred yet this year
    birth_date = datetime.date(birth_year, month, day)
    if birth_date > today:
        birth_date = birth_date.replace(year=birth_year - 1)
    
    return birth_date.strftime("%Y-%m-%d")

def generate_address():
    """Generate a realistic address."""
    state_code = random.choice(list(STATES.keys()))
    return {
        "line": [fake.street_address()],
        "city": fake.city(),
        "state": state_code,
        "zip": fake.postcode()
    }

def generate_telecom():
    """Generate telecommunication details."""
    return {
        "phone": fake.phone_number(),
        "email": fake.email()
    }

def generate_name(gender):
    """Generate name based on gender."""
    if gender == 'M':
        return fake.first_name_male(), fake.last_name()
    else:
        return fake.first_name_female(), fake.last_name()

def create_name_variant(first_name, last_name):
    """Create a realistic name variant (typo, nickname, etc.)."""
    variant_type = random.choice(['typo', 'nickname', 'hyphenated', 'maiden'])
    
    if variant_type == 'typo':
        # Simple character swap or deletion
        if len(first_name) > 3:
            pos = random.randint(1, len(first_name)-2)
            if random.random() < 0.5:
                # Swap characters
                chars = list(first_name)
                chars[pos], chars[pos+1] = chars[pos+1], chars[pos]
                return ''.join(chars), last_name
            else:
                # Delete a character
                return first_name[:pos] + first_name[pos+1:], last_name
        return first_name, last_name
    
    elif variant_type == 'nickname':
        # Common nicknames
        nicknames = {
            'Robert': ['Rob', 'Bob', 'Bobby'],
            'William': ['Will', 'Bill', 'Billy'],
            'Richard': ['Rick', 'Rich', 'Dick'],
            'Michael': ['Mike', 'Mikey'],
            'Christopher': ['Chris', 'Topher'],
            'Joseph': ['Joe', 'Joey'],
            'Thomas': ['Tom', 'Tommy'],
            'Charles': ['Chuck', 'Charlie'],
            'Elizabeth': ['Liz', 'Beth', 'Eliza', 'Lizzy'],
            'Margaret': ['Maggie', 'Meg', 'Peggy'],
            'Katherine': ['Kate', 'Katie', 'Kathy'],
            'Jennifer': ['Jen', 'Jenny'],
            'Patricia': ['Pat', 'Patty', 'Tricia'],
            'Stephanie': ['Steph', 'Steffy']
        }
        
        if first_name in nicknames:
            return random.choice(nicknames[first_name]), last_name
        return first_name, last_name
    
    elif variant_type == 'hyphenated':
        # Add a hyphenated last name
        return first_name, f"{last_name}-{fake.last_name()}"
    
    else:  # maiden name
        # Change last name completely
        return first_name, fake.last_name()

def create_address_variant(address):
    """Create a realistic address variant (abbreviation, typo, etc.)."""
    variant_address = address.copy()
    variant_type = random.choice(['abbreviation', 'typo', 'format'])
    
    if variant_type == 'abbreviation':
        # Abbreviate street type
        line = variant_address['line'][0]
        replacements = {
            'Street': 'St', 'Avenue': 'Ave', 'Boulevard': 'Blvd',
            'Drive': 'Dr', 'Road': 'Rd', 'Lane': 'Ln',
            'Place': 'Pl', 'Court': 'Ct', 'Circle': 'Cir'
        }
        for full, abbr in replacements.items():
            line = line.replace(f" {full}", f" {abbr}")
        variant_address['line'] = [line]
    
    elif variant_type == 'typo':
        # Simple typo in street name
        line = variant_address['line'][0]
        words = line.split()
        if len(words) > 1:
            word_idx = random.randint(0, len(words)-1)
            word = words[word_idx]
            if len(word) > 3:
                char_idx = random.randint(1, len(word)-2)
                # Swap two characters
                chars = list(word)
                chars[char_idx], chars[char_idx+1] = chars[char_idx+1], chars[char_idx]
                words[word_idx] = ''.join(chars)
                variant_address['line'] = [' '.join(words)]
    
    else:  # format
        # Change format (e.g., add/remove apartment number)
        line = variant_address['line'][0]
        if ' Apt ' in line or ' Unit ' in line:
            # Remove apartment/unit
            parts = line.split(' Apt ')
            if len(parts) == 1:
                parts = line.split(' Unit ')
            if len(parts) > 1:
                variant_address['line'] = [parts[0]]
        else:
            # Add apartment/unit
            variant_address['line'] = [f"{line} Apt {random.randint(1, 999)}"]
    
    return variant_address

def create_birthdate_variant(birthdate):
    """Create a realistic birthdate variant (typo, transposition)."""
    year, month, day = map(int, birthdate.split('-'))
    variant_type = random.choice(['day_off', 'month_day_swap', 'year_digit'])
    
    if variant_type == 'day_off':
        # Day off by 1-2
        day_change = random.choice([-2, -1, 1, 2])
        new_day = max(1, min(day + day_change, 28))  # Keep it simple, avoid month end issues
        return f"{year}-{month:02d}-{new_day:02d}"
    
    elif variant_type == 'month_day_swap':
        # Swap month and day if possible
        if month <= 12 and day <= 12:
            return f"{year}-{day:02d}-{month:02d}"
        return birthdate
    
    else:  # year_digit
        # Change one digit in the year
        year_str = str(year)
        pos = random.randint(0, 3)
        digit_change = random.choice([-1, 1])
        new_digit = (int(year_str[pos]) + digit_change) % 10
        year_list = list(year_str)
        year_list[pos] = str(new_digit)
        new_year = ''.join(year_list)
        return f"{new_year}-{month:02d}-{day:02d}"

def generate_patient_demographics(age=None, gender=None):
    """Generate complete patient demographics."""
    # Generate age if not provided
    if age is None:
        age = generate_age_based_on_distribution()
    
    # Generate gender if not provided
    if gender is None:
        gender = random.choice(['M', 'F'])
    
    # Generate name based on gender
    first_name, last_name = generate_name(gender)
    
    # Generate birthdate based on age
    birthdate = generate_birthdate(age)
    
    # Generate other demographic details
    race_items = list(RACES.items())
    race = weighted_choice(race_items)
    
    # Ensure consistency between race and ethnicity
    if race == 'hispanic':
        ethnicity = 'hispanic'
    else:
        ethnicity_items = list(ETHNICITIES.items())
        ethnicity = weighted_choice(ethnicity_items)
    
    # Generate marital status based on age
    if age < 18:
        marital_status = 'S'  # Children are always single
    else:
        marital_status_items = list(MARITAL_STATUS.items())
        marital_status = weighted_choice(marital_status_items)
    
    return {
        "first": first_name,
        "last": last_name,
        "gender": gender,
        "birthdate": birthdate,
        "address": generate_address(),
        "telecom": generate_telecom(),
        "race": race,
        "ethnicity": ethnicity,
        "marital_status": marital_status
    }

def generate_life_stages(demographics, num_stages=None):
    """Generate life stages (seeds) for a patient."""
    if num_stages is None:
        # Determine number of life stages based on age
        age = datetime.date.today().year - int(demographics["birthdate"][:4])
        if age < 25:
            num_stages = 1
        elif age < 50:
            num_stages = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
        else:
            num_stages = random.choices([1, 2, 3, 4], weights=[0.2, 0.3, 0.3, 0.2])[0]
    
    # Start with birth date
    birth_year = int(demographics["birthdate"][:4])
    birth_month = int(demographics["birthdate"][5:7])
    birth_day = int(demographics["birthdate"][8:10])
    
    # Create stage boundaries
    today = datetime.date.today()
    total_days = (today - datetime.date(birth_year, birth_month, birth_day)).days
    
    if num_stages == 1:
        stage_boundaries = [demographics["birthdate"], today.strftime("%Y-%m-%d")]
    else:
        # Create random boundaries between birth and today
        boundary_points = sorted([random.randint(0, total_days) for _ in range(num_stages - 1)])
        
        # Convert to dates
        stage_boundaries = [demographics["birthdate"]]
        birth_date = datetime.date(birth_year, birth_month, birth_day)
        
        for days in boundary_points:
            boundary_date = birth_date + datetime.timedelta(days=days)
            stage_boundaries.append(boundary_date.strftime("%Y-%m-%d"))
        
        stage_boundaries.append(today.strftime("%Y-%m-%d"))
    
    # Generate seeds for each life stage
    seeds = []
    current_demographics = demographics.copy()
    
    for i in range(num_stages):
        seed = {
            "start": stage_boundaries[i],
            "end": stage_boundaries[i+1],
            "demographics": current_demographics.copy()
        }
        
        # Add variants randomly
        if random.random() < 0.4:  # 40% chance of having variants
            seed["variants"] = generate_variants(current_demographics)
        
        seeds.append(seed)
        
        # Update demographics for next life stage if not the last stage
        if i < num_stages - 1:
            current_demographics = evolve_demographics(current_demographics)
    
    return seeds

def evolve_demographics(demographics):
    """Evolve demographics for a new life stage."""
    new_demographics = demographics.copy()
    
    # Possible changes: address, name (marriage), marital status
    
    # Address change
    if random.random() < LIFE_EVENTS['address_change']:
        new_demographics['address'] = generate_address()
    
    # Name change (especially for women after marriage)
    if random.random() < LIFE_EVENTS['name_change']:
        if demographics['gender'] == 'F' and demographics['marital_status'] == 'S':
            # Woman getting married might change last name
            new_demographics['last'] = fake.last_name()
            new_demographics['marital_status'] = 'M'
        elif random.random() < 0.1:  # Small chance of other name changes
            if random.random() < 0.5:
                # Hyphenated name
                new_demographics['last'] = f"{demographics['last']}-{fake.last_name()}"
            else:
                # Complete name change (rare)
                new_demographics['last'] = fake.last_name()
    
    # Marital status change
    if random.random() < LIFE_EVENTS['marital_status_change']:
        current_status = demographics['marital_status']
        if current_status == 'S':
            # Single -> Married
            new_demographics['marital_status'] = 'M'
        elif current_status == 'M':
            # Married -> Divorced or Widowed
            new_demographics['marital_status'] = random.choice(['D', 'W'])
        elif current_status == 'D':
            # Divorced -> Married
            new_demographics['marital_status'] = 'M'
    
    # Update contact info
    if random.random() < 0.5:  # 50% chance of updating contact info
        new_demographics['telecom'] = generate_telecom()
    
    return new_demographics

def generate_variants(demographics):
    """Generate variants for demographics."""
    variants = []
    
    # Determine how many variants to create (1-3)
    num_variants = random.randint(1, 3)
    
    for _ in range(num_variants):
        variant = {"demographics": {}}
        
        # Select which fields to vary
        fields_to_vary = random.sample([
            'name', 'address', 'birthdate', 'telecom'
        ], k=random.randint(1, 3))
        
        for field in fields_to_vary:
            if field == 'name':
                # Vary first name, last name, or both
                if random.random() < 0.5:
                    first_variant, last_variant = create_name_variant(
                        demographics['first'], demographics['last']
                    )
                    variant['demographics']['first'] = first_variant
                    variant['demographics']['last'] = last_variant
                else:
                    if random.random() < 0.5:
                        first_variant, _ = create_name_variant(
                            demographics['first'], demographics['last']
                        )
                        variant['demographics']['first'] = first_variant
                    else:
                        _, last_variant = create_name_variant(
                            demographics['first'], demographics['last']
                        )
                        variant['demographics']['last'] = last_variant
            
            elif field == 'address':
                variant['demographics']['address'] = create_address_variant(demographics['address'])
            
            elif field == 'birthdate':
                variant['demographics']['birthdate'] = create_birthdate_variant(demographics['birthdate'])
            
            elif field == 'telecom':
                # Create variant for phone or email
                variant_telecom = {}
                if random.random() < 0.5:
                    # Vary phone
                    phone = demographics['telecom']['phone']
                    # Simple variation: change a digit
                    digits = ''.join(c for c in phone if c.isdigit())
                    if digits:
                        pos = random.randint(0, len(digits)-1)
                        new_digit = str((int(digits[pos]) + random.randint(1, 9)) % 10)
                        new_digits = digits[:pos] + new_digit + digits[pos+1:]
                        variant_telecom['phone'] = phone.replace(digits, new_digits)
                else:
                    # Vary email
                    email = demographics['telecom']['email']
                    parts = email.split('@')
                    if len(parts) == 2:
                        username, domain = parts
                        if random.random() < 0.5:
                            # Add/remove a dot
                            if '.' in username:
                                username = username.replace('.', '')
                            else:
                                pos = random.randint(1, len(username)-1)
                                username = username[:pos] + '.' + username[pos:]
                        else:
                            # Typo in username
                            if len(username) > 3:
                                pos = random.randint(0, len(username)-1)
                                chars = list(username)
                                chars[pos] = random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
                                username = ''.join(chars)
                        variant_telecom['email'] = f"{username}@{domain}"
                
                if variant_telecom:
                    variant['demographics']['telecom'] = variant_telecom
        
        variants.append(variant)
    
    return variants

def generate_fixed_records(num_patients):
    """Generate fixed records for the specified number of patients."""
    fixed_records = []
    
    for i in range(num_patients):
        # Generate base demographics
        demographics = generate_patient_demographics()
        
        # Generate life stages
        seeds = generate_life_stages(demographics)
        
        # Create patient record
        patient = {
            "individualId": f"patient-{i+1:06d}",
            "gender": demographics["gender"],
            "dateOfBirth": demographics["birthdate"],
            "seeds": []
        }
        
        # Add proper seed information
        for j, seed in enumerate(seeds):
            # Extract data from the seed
            start_date = seed["start"]
            end_date = seed["end"]
            demo = seed["demographics"]
            
            # Create a properly formatted seed
            formatted_seed = {
                "seedId": f"seed-{i+1:06d}-{j+1:02d}",
                "start": start_date,
                "end": end_date,
                "period": {
                    "start": start_date,
                    "end": end_date
                },
                "state": demo["address"]["state"],
                "city": demo["address"]["city"],
                "addressLines": demo["address"]["line"],
                "zipCode": demo["address"]["zip"],
                "givenName": demo["first"],
                "familyName": demo["last"],
                "demographics": demo
            }
            
            # Add variants if they exist
            if "variants" in seed:
                formatted_seed["variants"] = seed["variants"]
            else:
                formatted_seed["variants"] = []
            
            # Add the formatted seed to the patient
            patient["seeds"].append(formatted_seed)
        
        fixed_records.append(patient)
    
    return fixed_records

def main():
    """Main function to parse arguments and generate data."""
    parser = argparse.ArgumentParser(description='Generate synthetic patient data for Synthea.')
    parser.add_argument('--num_patients', type=int, default=10, help='Number of patients to generate')
    parser.add_argument('--output', type=str, default='fixed_records.json', help='Output JSON file')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)
    
    # Generate fixed records
    fixed_records = generate_fixed_records(args.num_patients)
    
    # Format as expected by Synthea (object with 'records' key)
    synthea_format = {"records": fixed_records}
    
    # Write to file
    with open(args.output, 'w') as f:
        json.dump(synthea_format, f, indent=2)
    
    print(f"Generated {args.num_patients} patient records in {args.output}")

if __name__ == "__main__":
    main()