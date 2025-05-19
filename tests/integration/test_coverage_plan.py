"""
Integration test for CoveragePlan model.
"""
import pytest
from datetime import date, timedelta
import os
import sys
import uuid
import json

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from health_insurance_au.utils.db_utils import execute_query, execute_non_query
from health_insurance_au.models.models import CoveragePlan


class TestCoveragePlanIntegration:
    """Integration tests for CoveragePlan model."""
    
    def test_create_and_retrieve_coverage_plan(self):
        """Test creating and retrieving a coverage plan."""
        # Generate a unique plan code
        plan_code = f"TST{uuid.uuid4().hex[:8].upper()}"
        
        # Create a coverage plan
        plan = CoveragePlan(
            plan_code=plan_code,
            plan_name="Test Plan",
            plan_type="Combined",
            monthly_premium=150.0,
            annual_premium=1800.0,
            effective_date=date.today() - timedelta(days=30),
            hospital_tier="Silver",
            excess_options=[250, 500, 750],
            waiting_periods={"general": 2, "pre_existing": 12, "pregnancy": 12},
            coverage_details={"description": "Test plan for integration testing"}
        )
        
        try:
            # Convert to dictionary for database insertion
            plan_dict = plan.to_dict()
            
            # Add LastModified field
            plan_dict['LastModified'] = date.today()
            
            # Construct SQL query
            columns = ', '.join(plan_dict.keys())
            placeholders = ', '.join(['?'] * len(plan_dict))
            values = tuple(plan_dict.values())
            
            # Insert into database
            execute_non_query(f"""
            INSERT INTO Insurance.CoveragePlans ({columns})
            VALUES ({placeholders})
            """, values)
            
            # Retrieve from database
            result = execute_query("""
            SELECT * FROM Insurance.CoveragePlans WHERE PlanCode = ?
            """, (plan_code,))
            
            # Assert plan was inserted correctly
            assert len(result) == 1
            assert result[0]['PlanName'] == "Test Plan"
            assert result[0]['PlanCode'] == plan_code
            assert result[0]['PlanType'] == "Combined"
            assert float(result[0]['MonthlyPremium']) == 150.0
            
            # Check JSON fields
            excess_options = json.loads(result[0]['ExcessOptions'])
            assert 250 in excess_options
            assert 500 in excess_options
            assert 750 in excess_options
            
            waiting_periods = json.loads(result[0]['WaitingPeriods'])
            assert waiting_periods['general'] == 2
            assert waiting_periods['pre_existing'] == 12
            
            coverage_details = json.loads(result[0]['CoverageDetails'])
            assert coverage_details['description'] == "Test plan for integration testing"
            
        finally:
            # Clean up
            execute_non_query("""
            DELETE FROM Insurance.CoveragePlans WHERE PlanCode = ?
            """, (plan_code,))