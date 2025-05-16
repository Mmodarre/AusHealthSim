from datetime import date
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
cursor.execute('SELECT PolicyID, PolicyNumber, NextPremiumDueDate, LastModified FROM Insurance.Policies WHERE YEAR(NextPremiumDueDate) = 2025 ORDER BY PolicyID')
rows = cursor.fetchall()
print("Policies with premium due dates in 2025:")
for row in rows[:5]:
    print(f"PolicyID: {row[0]}, PolicyNumber: {row[1]}, NextPremiumDueDate: {row[2]}, LastModified: {row[3]}")

cursor.execute('SELECT MIN(LastModified) as MinDate, MAX(LastModified) as MaxDate FROM Insurance.Policies WHERE YEAR(NextPremiumDueDate) = 2025')
date_range = cursor.fetchone()
print(f"\nLastModified date range for 2025 policies: Min={date_range[0]}, Max={date_range[1]}")

conn.close()