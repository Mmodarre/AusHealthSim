from datetime import date
from health_insurance_au.simulation.simulation import HealthInsuranceSimulation
import pyodbc
from health_insurance_au.config import DB_CONFIG

# Create a simulation instance
sim = HealthInsuranceSimulation()

# Set a specific policy and date
policy_number = "POL-VIC-290487"
simulation_date = date(2025, 6, 2)

print(f"Running simulation for policy {policy_number} on date {simulation_date}")

# Connect to the database
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

# Check the policy before update
cursor.execute(f"SELECT PolicyID, LastPremiumPaidDate, NextPremiumDueDate, LastModified FROM Insurance.Policies WHERE PolicyNumber = '{policy_number}'")
row = cursor.fetchone()
print("\nBefore update:")
print(f"  Policy ID: {row[0]}")
print(f"  Last premium paid date: {row[1]}")
print(f"  Next premium due date: {row[2]}")
print(f"  Last modified date: {row[3]}")

# Load data and process the payment
sim.load_data_from_db()
sim.process_premium_payments(simulation_date)
print("Premium payments processed")

# Check the policy after update
cursor.execute(f"SELECT PolicyID, LastPremiumPaidDate, NextPremiumDueDate, LastModified FROM Insurance.Policies WHERE PolicyNumber = '{policy_number}'")
row = cursor.fetchone()
print("\nAfter update:")
print(f"  Policy ID: {row[0]}")
print(f"  Last premium paid date: {row[1]}")
print(f"  Next premium due date: {row[2]}")
print(f"  Last modified date: {row[3]}")

conn.close()