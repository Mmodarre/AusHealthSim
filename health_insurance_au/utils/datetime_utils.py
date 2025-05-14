"""
Datetime utilities for the Health Insurance AU simulation.
"""
import random
from datetime import datetime, time

def generate_random_datetime(date_value):
    """Generate a random datetime within the given date."""
    # Business hours (8 AM to 5 PM)
    random_hour = random.randint(8, 17)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    return datetime.combine(date_value, time(random_hour, random_minute, random_second))

# Apply this function to convert dates to datetimes in the claims.py module
# Example usage:
# service_date = generate_random_datetime(service_date)