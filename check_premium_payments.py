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

# Check premium payments for the policy
policy_number = "POL-VIC-290487"

cursor.execute(f"""
    SELECT p.PaymentID, p.PolicyID, p.PaymentDate, p.PaymentAmount, p.PaymentMethod, p.PaymentReference, p.PaymentStatus, p.LastModified
    FROM Insurance.PremiumPayments p
    JOIN Insurance.Policies pol ON p.PolicyID = pol.PolicyID
    WHERE pol.PolicyNumber = '{policy_number}'
    ORDER BY p.PaymentDate DESC
""")

rows = cursor.fetchall()
print(f"Premium payments for policy {policy_number}:")
for row in rows:
    print(f"  Payment ID: {row[0]}")
    print(f"  Policy ID: {row[1]}")
    print(f"  Payment Date: {row[2]}")
    print(f"  Payment Amount: {row[3]}")
    print(f"  Payment Method: {row[4]}")
    print(f"  Payment Reference: {row[5]}")
    print(f"  Payment Status: {row[6]}")
    print(f"  Last Modified: {row[7]}")
    print("---")

# Check the history of LastModified dates for this policy
cursor.execute(f"""
    SELECT name FROM sys.tables WHERE schema_id = SCHEMA_ID('Insurance')
""")

tables = cursor.fetchall()
print(f"\nTables in Insurance schema:")
for table in tables:
    print(f"  {table[0]}")

conn.close()