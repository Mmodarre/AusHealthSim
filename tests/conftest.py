"""
Configuration for pytest.
"""
import os
import sys
import pytest
from datetime import date

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

@pytest.fixture(scope="session")
def simulation_date():
    """Fixture to provide a consistent simulation date for tests."""
    return date(2022, 4, 15)

@pytest.fixture(scope="session")
def db_connection():
    """Fixture to provide a database connection for tests."""
    from health_insurance_au.utils.db_utils import get_connection
    with get_connection() as conn:
        yield conn