from datetime import date
from health_insurance_au.simulation.simulation import HealthInsuranceSimulation

# Create a simulation instance
sim = HealthInsuranceSimulation()

# Load data from the database
sim.load_data_from_db()
print(f"Loaded {len(sim.policies)} policies")

# Find a policy with a premium due date in 2025
test_policy = None
for policy in sim.policies:
    if policy.next_premium_due_date and policy.next_premium_due_date.year == 2025:
        test_policy = policy
        break

if test_policy:
    print(f"Found policy {test_policy.policy_number} with premium due date {test_policy.next_premium_due_date}")
    
    # Set the simulation date to the premium due date
    simulation_date = test_policy.next_premium_due_date
    print(f"Running simulation for date {simulation_date}")
    
    # Process premium payments for this date
    sim.process_premium_payments(simulation_date)
    print("Premium payments processed")
    
    # Check the updated policy
    sim = HealthInsuranceSimulation()
    sim.load_data_from_db()
    
    # Find the same policy again
    updated_policy = None
    for policy in sim.policies:
        if policy.policy_number == test_policy.policy_number:
            updated_policy = policy
            break
    
    if updated_policy:
        print(f"Updated policy {updated_policy.policy_number}:")
        print(f"  Last premium paid date: {updated_policy.last_premium_paid_date}")
        print(f"  Next premium due date: {updated_policy.next_premium_due_date}")
        
        # Check the database directly
        import pyodbc
        from health_insurance_au.config import DB_CONFIG
        
        conn_str = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
            f"TrustServerCertificate=yes;"
        )
        
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        cursor.execute(f"SELECT LastPremiumPaidDate, NextPremiumDueDate, LastModified FROM Insurance.Policies WHERE PolicyNumber = '{updated_policy.policy_number}'")
        row = cursor.fetchone()
        
        print("\nDatabase values:")
        print(f"  Last premium paid date: {row[0]}")
        print(f"  Next premium due date: {row[1]}")
        print(f"  Last modified date: {row[2]}")
        
        conn.close()
else:
    print("No policies with premium due dates in 2025 found")