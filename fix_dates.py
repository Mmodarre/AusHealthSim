from datetime import date
import pyodbc
from health_insurance_au.config import DB_CONFIG
from health_insurance_au.utils.db_utils import execute_non_query

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

# Update all policies with premium due dates in 2025 to have LastModified in 2022
update_date = date(2022, 5, 16)
print(f"Updating policies with premium due dates in 2025 to have LastModified = {update_date}")

# First, get the list of policies to update
cursor.execute("SELECT PolicyID, PolicyNumber FROM Insurance.Policies WHERE YEAR(NextPremiumDueDate) = 2025")
policies = cursor.fetchall()
print(f"Found {len(policies)} policies to update")

# Update each policy
for policy in policies:
    policy_id = policy[0]
    policy_number = policy[1]
    
    try:
        query = """
        UPDATE Insurance.Policies
        SET LastModified = ?
        WHERE PolicyID = ?
        """
        cursor.execute(query, (update_date, policy_id))
        print(f"Updated policy {policy_number} (ID: {policy_id})")
    except Exception as e:
        print(f"Error updating policy {policy_number}: {e}")

# Update premium payments as well
cursor.execute("SELECT PaymentID FROM Insurance.PremiumPayments WHERE YEAR(PaymentDate) = 2025")
payments = cursor.fetchall()
print(f"\nFound {len(payments)} premium payments to update")

for payment in payments:
    payment_id = payment[0]
    
    try:
        query = """
        UPDATE Insurance.PremiumPayments
        SET LastModified = ?
        WHERE PaymentID = ?
        """
        cursor.execute(query, (update_date, payment_id))
        print(f"Updated payment ID: {payment_id}")
    except Exception as e:
        print(f"Error updating payment {payment_id}: {e}")

conn.close()
print("\nUpdate completed")