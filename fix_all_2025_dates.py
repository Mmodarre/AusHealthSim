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

# Update date to use
update_date = date(2022, 5, 16)
print(f"Updating all policies with premium due dates in 2025 to have LastModified = {update_date}")

# Update policies with premium due dates in 2025
try:
    cursor.execute(
        "UPDATE Insurance.Policies SET LastModified = ? WHERE YEAR(NextPremiumDueDate) = 2025", 
        update_date
    )
    print(f"Updated {cursor.rowcount} policies")
except Exception as e:
    print(f"Error updating policies: {e}")

# Update premium payments with payment dates in 2025
try:
    cursor.execute(
        "UPDATE Insurance.PremiumPayments SET LastModified = ? WHERE YEAR(PaymentDate) = 2025", 
        update_date
    )
    print(f"Updated {cursor.rowcount} premium payments")
except Exception as e:
    print(f"Error updating premium payments: {e}")

# Verify a sample of the updates
cursor.execute("""
    SELECT TOP 5 p.PolicyID, p.PolicyNumber, p.NextPremiumDueDate, p.LastModified 
    FROM Insurance.Policies p 
    WHERE YEAR(p.NextPremiumDueDate) = 2025
    ORDER BY p.PolicyID
""")

print("\nVerification (Policies):")
for row in cursor.fetchall():
    print(f"Policy {row[0]} ({row[1]}): NextPremiumDueDate={row[2]}, LastModified={row[3]}")

cursor.execute("""
    SELECT TOP 5 pp.PaymentID, pp.PaymentDate, pp.LastModified 
    FROM Insurance.PremiumPayments pp 
    WHERE YEAR(pp.PaymentDate) = 2025
    ORDER BY pp.PaymentID
""")

print("\nVerification (Premium Payments):")
for row in cursor.fetchall():
    print(f"Payment {row[0]}: PaymentDate={row[1]}, LastModified={row[2]}")

conn.close()
print("\nUpdate completed")