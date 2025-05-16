from datetime import date
import pyodbc
from health_insurance_au.config import DB_CONFIG

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

# Update specific policies
update_date = date(2022, 5, 16)
policy_ids = [1, 2, 3, 4, 6]  # IDs from our earlier query

print(f"Updating specific policies to have LastModified = {update_date}")

for policy_id in policy_ids:
    try:
        # Get the policy number first
        cursor.execute("SELECT PolicyNumber FROM Insurance.Policies WHERE PolicyID = ?", policy_id)
        policy_number = cursor.fetchone()[0]
        
        # Update the policy
        cursor.execute(
            "UPDATE Insurance.Policies SET LastModified = ? WHERE PolicyID = ?", 
            (update_date, policy_id)
        )
        print(f"Updated policy {policy_number} (ID: {policy_id})")
    except Exception as e:
        print(f"Error updating policy ID {policy_id}: {e}")

# Update the first premium payment
try:
    cursor.execute(
        "UPDATE Insurance.PremiumPayments SET LastModified = ? WHERE PaymentID = 1", 
        update_date
    )
    print("Updated payment ID: 1")
except Exception as e:
    print(f"Error updating payment: {e}")

# Verify the updates
cursor.execute("""
    SELECT p.PolicyID, p.PolicyNumber, p.NextPremiumDueDate, p.LastModified 
    FROM Insurance.Policies p 
    WHERE p.PolicyID IN (1, 2, 3, 4, 6)
""")

print("\nVerification:")
for row in cursor.fetchall():
    print(f"Policy {row[0]} ({row[1]}): NextPremiumDueDate={row[2]}, LastModified={row[3]}")

cursor.execute("SELECT PaymentID, LastModified FROM Insurance.PremiumPayments WHERE PaymentID = 1")
payment = cursor.fetchone()
if payment:
    print(f"Payment 1: LastModified={payment[1]}")

conn.close()
print("\nUpdate completed")