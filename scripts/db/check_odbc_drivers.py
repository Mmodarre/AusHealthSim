"""
Check available ODBC drivers on Windows system.
This script lists all ODBC drivers installed on the system.
"""
import sys
import pyodbc

def main():
    print("Checking available ODBC drivers on this system:")
    print("-" * 50)
    
    try:
        drivers = pyodbc.drivers()
        if drivers:
            print("Found the following ODBC drivers:")
            for i, driver in enumerate(drivers, 1):
                print(f"{i}. {driver}")
        else:
            print("No ODBC drivers found.")
            
        print("\nRecommended driver for SQL Server:")
        print("- For SQL Server 2022: {ODBC Driver 18 for SQL Server}")
        print("- For SQL Server 2019: {ODBC Driver 17 for SQL Server}")
        print("- For older versions: {SQL Server}")
            
    except Exception as e:
        print(f"Error checking ODBC drivers: {e}")
    
    print("\nPlease update your db_config.env file with the correct driver.")
    print("Example: DB_DRIVER={ODBC Driver 17 for SQL Server}")

if __name__ == "__main__":
    main()