"""
Initialize the Health Insurance AU database with CDC support using pyodbc.
"""
import argparse
import logging
import sys
import os
import pyodbc
from contextlib import contextmanager
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_insurance_au.utils.env_utils import get_db_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@contextmanager
def get_connection(server, username, password, database=None):
    """Context manager for database connections."""
    # Construct connection string with the correct driver name
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};UID={username};PWD={password};TrustServerCertificate=yes"
    if database:
        conn_str += f";DATABASE={database}"
    
    conn = None
    try:
        conn = pyodbc.connect(conn_str, autocommit=True)  # Set autocommit to True
        yield conn
    except pyodbc.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def execute_sql(conn, query, params=None):
    """Execute a SQL query with parameters."""
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        # No need to commit with autocommit=True
        return cursor
    except pyodbc.Error as e:
        logger.error(f"SQL execution error: {e}")
        raise

def execute_script(conn, script):
    """Execute a SQL script with multiple statements."""
    # Split script by GO statements (common in SQL Server scripts)
    statements = script.split("GO")
    
    for statement in statements:
        if statement.strip():
            try:
                cursor = conn.cursor()
                cursor.execute(statement)
                # No need to commit with autocommit=True
            except pyodbc.Error as e:
                logger.error(f"SQL script execution error: {e}")
                logger.error(f"Failed statement: {statement}")
                raise

def check_database_exists(server, username, password, database):
    """Check if the database exists."""
    try:
        with get_connection(server, username, password) as conn:
            cursor = execute_sql(conn, "SELECT name FROM sys.databases WHERE name = ?", (database,))
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        logger.error(f"Error checking database existence: {e}")
        return False

def create_database(server, username, password, database):
    """Create a new database."""
    try:
        with get_connection(server, username, password) as conn:
            execute_sql(conn, f"CREATE DATABASE {database}")
            logger.info(f"Database {database} created")
            return True
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False

def drop_database(server, username, password, database):
    """Drop an existing database."""
    try:
        with get_connection(server, username, password) as conn:
            # Ensure no active connections to the database
            execute_sql(conn, f"ALTER DATABASE {database} SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
            execute_sql(conn, f"DROP DATABASE {database}")
            logger.info(f"Database {database} dropped")
            return True
    except Exception as e:
        logger.error(f"Error dropping database: {e}")
        return False

def create_schema(conn, schema_name):
    """Create a schema if it doesn't exist."""
    try:
        execute_sql(conn, f"IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema_name}') EXEC('CREATE SCHEMA {schema_name}')")
        logger.info(f"Schema {schema_name} created (if it didn't exist)")
        return True
    except Exception as e:
        logger.error(f"Error creating schema {schema_name}: {e}")
        return False

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Initialize the Health Insurance AU database')
    parser.add_argument('--server', help='SQL Server address')
    parser.add_argument('--username', help='SQL Server username')
    parser.add_argument('--password', help='SQL Server password')
    parser.add_argument('--database', help='Database name')
    parser.add_argument('--drop', action='store_true', help='Drop the database if it exists')
    parser.add_argument('--env-file', help='Path to environment file with database credentials')
    
    args = parser.parse_args()
    
    # Get database configuration from environment variables or file
    db_config = get_db_config(args.env_file)
    
    # Override with command-line arguments if provided
    server = args.server or db_config['server']
    username = args.username or db_config['username']
    password = args.password or db_config['password']
    database = args.database or db_config['database']
    
    # Validate required parameters
    if not server:
        logger.error("Server address is required")
        return
    if not username:
        logger.error("Username is required")
        return
    if not password:
        logger.error("Password is required")
        return
    if not database:
        logger.error("Database name is required")
        return
    
    # Check if the database exists
    logger.info(f"Checking if database {database} exists...")
    database_exists = check_database_exists(server, username, password, database)
    
    if database_exists:
        logger.info(f"Database {database} already exists")
        
        if args.drop:
            logger.info(f"Dropping database {database}...")
            if not drop_database(server, username, password, database):
                logger.error("Failed to drop database, exiting")
                return
            database_exists = False
    
    if not database_exists:
        logger.info(f"Creating database {database}...")
        if not create_database(server, username, password, database):
            logger.error("Failed to create database, exiting")
            return
    
    # Create schemas and tables
    try:
        with get_connection(server, username, password, database) as conn:
            # Create schemas
            logger.info("Creating schemas...")
            for schema in ['Insurance', 'Simulation', 'Integration', 'Regulatory']:
                create_schema(conn, schema)
            
            # Create tables
            logger.info("Creating tables...")
            
            # Insurance.Members
            execute_script(conn, """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Insurance.Members') AND type in (N'U'))
            CREATE TABLE Insurance.Members (
                MemberID INT IDENTITY(1,1) PRIMARY KEY,
                MemberNumber VARCHAR(20) NOT NULL,
                Title VARCHAR(10) NULL,
                FirstName VARCHAR(50) NOT NULL,
                LastName VARCHAR(50) NOT NULL,
                DateOfBirth DATE NOT NULL,
                Gender VARCHAR(10) NOT NULL,
                Email VARCHAR(100) NULL,
                MobilePhone VARCHAR(20) NULL,
                HomePhone VARCHAR(20) NULL,
                AddressLine1 VARCHAR(100) NOT NULL,
                AddressLine2 VARCHAR(100) NULL,
                City VARCHAR(50) NOT NULL,
                State VARCHAR(3) NOT NULL,
                PostCode VARCHAR(10) NOT NULL,
                Country VARCHAR(50) NOT NULL DEFAULT 'Australia',
                MedicareNumber VARCHAR(15) NULL,
                LHCLoadingPercentage DECIMAL(5,2) DEFAULT 0.00,
                PHIRebateTier VARCHAR(10) DEFAULT 'Base',
                JoinDate DATE NOT NULL DEFAULT GETDATE(),
                IsActive BIT NOT NULL DEFAULT 1,
                LastModified DATETIME2 NOT NULL DEFAULT GETDATE()
            )
            """)
            
            # Insurance.CoveragePlans
            execute_script(conn, """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Insurance.CoveragePlans') AND type in (N'U'))
            CREATE TABLE Insurance.CoveragePlans (
                PlanID INT IDENTITY(1,1) PRIMARY KEY,
                PlanCode VARCHAR(20) NOT NULL,
                PlanName VARCHAR(100) NOT NULL,
                PlanType VARCHAR(20) NOT NULL,
                HospitalTier VARCHAR(20) NULL,
                MonthlyPremium DECIMAL(10,2) NOT NULL,
                AnnualPremium DECIMAL(10,2) NOT NULL,
                ExcessOptions VARCHAR(100) NULL,
                WaitingPeriods VARCHAR(500) NULL,
                CoverageDetails VARCHAR(MAX) NULL,
                IsActive BIT NOT NULL DEFAULT 1,
                EffectiveDate DATE NOT NULL,
                EndDate DATE NULL,
                LastModified DATETIME2 NOT NULL DEFAULT GETDATE()
            )
            """)
            
            # Insurance.Policies
            execute_script(conn, """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Insurance.Policies') AND type in (N'U'))
            CREATE TABLE Insurance.Policies (
                PolicyID INT IDENTITY(1,1) PRIMARY KEY,
                PolicyNumber VARCHAR(20) NOT NULL,
                PrimaryMemberID INT NOT NULL,
                PlanID INT NOT NULL,
                CoverageType VARCHAR(20) NOT NULL,
                StartDate DATE NOT NULL,
                EndDate DATE NULL,
                ExcessAmount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                PremiumFrequency VARCHAR(20) NOT NULL DEFAULT 'Monthly',
                CurrentPremium DECIMAL(10,2) NOT NULL,
                RebatePercentage DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                LHCLoadingPercentage DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                Status VARCHAR(20) NOT NULL DEFAULT 'Active',
                PaymentMethod VARCHAR(20) NOT NULL DEFAULT 'Direct Debit',
                LastPremiumPaidDate DATE NULL,
                NextPremiumDueDate DATE NULL,
                LastModified DATETIME2 NOT NULL DEFAULT GETDATE(),
                CONSTRAINT FK_Policies_Members FOREIGN KEY (PrimaryMemberID) REFERENCES Insurance.Members (MemberID),
                CONSTRAINT FK_Policies_Plans FOREIGN KEY (PlanID) REFERENCES Insurance.CoveragePlans (PlanID)
            )
            """)
            
            # Insurance.PolicyMembers
            execute_script(conn, """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Insurance.PolicyMembers') AND type in (N'U'))
            CREATE TABLE Insurance.PolicyMembers (
                PolicyMemberID INT IDENTITY(1,1) PRIMARY KEY,
                PolicyID INT NOT NULL,
                MemberID INT NOT NULL,
                RelationshipToPrimary VARCHAR(20) NOT NULL,
                StartDate DATE NOT NULL,
                EndDate DATE NULL,
                IsActive BIT NOT NULL DEFAULT 1,
                LastModified DATETIME2 NOT NULL DEFAULT GETDATE(),
                CONSTRAINT FK_PolicyMembers_Policies FOREIGN KEY (PolicyID) REFERENCES Insurance.Policies (PolicyID),
                CONSTRAINT FK_PolicyMembers_Members FOREIGN KEY (MemberID) REFERENCES Insurance.Members (MemberID),
                CONSTRAINT UQ_PolicyMembers_PolicyMember UNIQUE (PolicyID, MemberID)
            )
            """)
            
            # Insurance.Providers
            execute_script(conn, """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Insurance.Providers') AND type in (N'U'))
            CREATE TABLE Insurance.Providers (
                ProviderID INT IDENTITY(1,1) PRIMARY KEY,
                ProviderNumber VARCHAR(20) NOT NULL,
                ProviderName VARCHAR(100) NOT NULL,
                ProviderType VARCHAR(50) NOT NULL,
                AddressLine1 VARCHAR(100) NOT NULL,
                AddressLine2 VARCHAR(100) NULL,
                City VARCHAR(50) NOT NULL,
                State VARCHAR(3) NOT NULL,
                PostCode VARCHAR(10) NOT NULL,
                Country VARCHAR(50) NOT NULL DEFAULT 'Australia',
                Phone VARCHAR(20) NULL,
                Email VARCHAR(100) NULL,
                IsPreferredProvider BIT NOT NULL DEFAULT 0,
                AgreementStartDate DATE NULL,
                AgreementEndDate DATE NULL,
                IsActive BIT NOT NULL DEFAULT 1,
                LastModified DATETIME2 NOT NULL DEFAULT GETDATE()
            )
            """)
            
            # Insurance.Claims
            execute_script(conn, """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Insurance.Claims') AND type in (N'U'))
            CREATE TABLE Insurance.Claims (
                ClaimID INT IDENTITY(1,1) PRIMARY KEY,
                ClaimNumber VARCHAR(20) NOT NULL,
                PolicyID INT NOT NULL,
                MemberID INT NOT NULL,
                ProviderID INT NOT NULL,
                ServiceDate DATE NOT NULL,
                SubmissionDate DATE NOT NULL,
                ClaimType VARCHAR(20) NOT NULL,
                ServiceDescription VARCHAR(200) NOT NULL,
                MBSItemNumber VARCHAR(20) NULL,
                ChargedAmount DECIMAL(10,2) NOT NULL,
                MedicareAmount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                InsuranceAmount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                GapAmount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                ExcessApplied DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                Status VARCHAR(20) NOT NULL DEFAULT 'Submitted',
                ProcessedDate DATE NULL,
                PaymentDate DATE NULL,
                RejectionReason VARCHAR(200) NULL,
                LastModified DATETIME2 NOT NULL DEFAULT GETDATE(),
                CONSTRAINT FK_Claims_Policies FOREIGN KEY (PolicyID) REFERENCES Insurance.Policies (PolicyID),
                CONSTRAINT FK_Claims_Members FOREIGN KEY (MemberID) REFERENCES Insurance.Members (MemberID),
                CONSTRAINT FK_Claims_Providers FOREIGN KEY (ProviderID) REFERENCES Insurance.Providers (ProviderID)
            )
            """)
            
            # Insurance.PremiumPayments
            execute_script(conn, """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Insurance.PremiumPayments') AND type in (N'U'))
            CREATE TABLE Insurance.PremiumPayments (
                PaymentID INT IDENTITY(1,1) PRIMARY KEY,
                PolicyID INT NOT NULL,
                PaymentDate DATE NOT NULL,
                PaymentAmount DECIMAL(10,2) NOT NULL,
                PaymentMethod VARCHAR(20) NOT NULL,
                PaymentReference VARCHAR(50) NULL,
                PaymentStatus VARCHAR(20) NOT NULL DEFAULT 'Successful',
                PeriodStartDate DATE NOT NULL,
                PeriodEndDate DATE NOT NULL,
                LastModified DATETIME2 NOT NULL DEFAULT GETDATE(),
                CONSTRAINT FK_PremiumPayments_Policies FOREIGN KEY (PolicyID) REFERENCES Insurance.Policies (PolicyID)
            )
            """)
            
            # Regulatory.PHIRebateTiers
            execute_script(conn, """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Regulatory.PHIRebateTiers') AND type in (N'U'))
            CREATE TABLE Regulatory.PHIRebateTiers (
                TierID INT IDENTITY(1,1) PRIMARY KEY,
                TierName VARCHAR(20) NOT NULL,
                IncomeThresholdSingle DECIMAL(10,2) NOT NULL,
                IncomeThresholdFamily DECIMAL(10,2) NOT NULL,
                RebatePercentageUnder65 DECIMAL(5,2) NOT NULL,
                RebatePercentage65to69 DECIMAL(5,2) NOT NULL,
                RebatePercentage70Plus DECIMAL(5,2) NOT NULL,
                EffectiveDate DATE NOT NULL,
                EndDate DATE NULL,
                LastModified DATETIME2 NOT NULL DEFAULT GETDATE()
            )
            """)
            
            # Regulatory.MBSItems
            execute_script(conn, """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Regulatory.MBSItems') AND type in (N'U'))
            CREATE TABLE Regulatory.MBSItems (
                ItemID INT IDENTITY(1,1) PRIMARY KEY,
                MBSItemNumber VARCHAR(20) NOT NULL,
                Description VARCHAR(500) NOT NULL,
                Category VARCHAR(100) NOT NULL,
                ScheduleFee DECIMAL(10,2) NOT NULL,
                MedicareBenefit DECIMAL(10,2) NOT NULL,
                EffectiveDate DATE NOT NULL,
                EndDate DATE NULL,
                LastModified DATETIME2 NOT NULL DEFAULT GETDATE()
            )
            """)
            
            # Integration.SyntheaPatients
            execute_script(conn, """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Integration.SyntheaPatients') AND type in (N'U'))
            CREATE TABLE Integration.SyntheaPatients (
                SyntheaPatientID INT IDENTITY(1,1) PRIMARY KEY,
                PatientFHIRID VARCHAR(100) NOT NULL,
                MemberID INT NULL,
                PatientData NVARCHAR(MAX) NOT NULL,
                ImportDate DATETIME2 NOT NULL DEFAULT GETDATE(),
                LastModified DATETIME2 NOT NULL DEFAULT GETDATE(),
                CONSTRAINT FK_SyntheaPatients_Members FOREIGN KEY (MemberID) REFERENCES Insurance.Members (MemberID)
            )
            """)
            
            # Integration.SyntheaEncounters
            execute_script(conn, """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Integration.SyntheaEncounters') AND type in (N'U'))
            CREATE TABLE Integration.SyntheaEncounters (
                SyntheaEncounterID INT IDENTITY(1,1) PRIMARY KEY,
                EncounterFHIRID VARCHAR(100) NOT NULL,
                PatientFHIRID VARCHAR(100) NOT NULL,
                ClaimID INT NULL,
                EncounterData NVARCHAR(MAX) NOT NULL,
                ImportDate DATETIME2 NOT NULL DEFAULT GETDATE(),
                LastModified DATETIME2 NOT NULL DEFAULT GETDATE(),
                CONSTRAINT FK_SyntheaEncounters_Claims FOREIGN KEY (ClaimID) REFERENCES Insurance.Claims (ClaimID)
            )
            """)
            
            # Integration.SyntheaProcedures
            execute_script(conn, """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Integration.SyntheaProcedures') AND type in (N'U'))
            CREATE TABLE Integration.SyntheaProcedures (
                SyntheaProcedureID INT IDENTITY(1,1) PRIMARY KEY,
                ProcedureFHIRID VARCHAR(100) NOT NULL,
                PatientFHIRID VARCHAR(100) NOT NULL,
                EncounterFHIRID VARCHAR(100) NOT NULL,
                ClaimID INT NULL,
                ProcedureData NVARCHAR(MAX) NOT NULL,
                ImportDate DATETIME2 NOT NULL DEFAULT GETDATE(),
                LastModified DATETIME2 NOT NULL DEFAULT GETDATE(),
                CONSTRAINT FK_SyntheaProcedures_Claims FOREIGN KEY (ClaimID) REFERENCES Insurance.Claims (ClaimID)
            )
            """)
            
            # Create stored procedures
            logger.info("Creating stored procedures...")
            
            # Simulation.AddMembers
            execute_script(conn, """
            IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Simulation.AddMembers') AND type in (N'P'))
                DROP PROCEDURE Simulation.AddMembers
            """)
            execute_script(conn, """
            CREATE PROCEDURE Simulation.AddMembers
                @NumberOfMembers INT = 10
            AS
            BEGIN
                SET NOCOUNT ON;
                
                -- This is a placeholder procedure that will be implemented in Python
                -- The Python application will read from health_insurance_demo_10k.json
                -- and insert the data into the Insurance.Members table
                
                PRINT 'Adding ' + CAST(@NumberOfMembers AS VARCHAR) + ' new members';
            END
            """)
            
            # Simulation.AddCoveragePlans
            execute_script(conn, """
            IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Simulation.AddCoveragePlans') AND type in (N'P'))
                DROP PROCEDURE Simulation.AddCoveragePlans
            """)
            execute_script(conn, """
            CREATE PROCEDURE Simulation.AddCoveragePlans
                @NumberOfPlans INT = 5
            AS
            BEGIN
                SET NOCOUNT ON;
                
                -- This is a placeholder procedure that will be implemented in Python
                -- The Python application will create realistic health insurance plans
                -- based on Bupa.com.au and insert them into the Insurance.CoveragePlans table
                
                PRINT 'Adding ' + CAST(@NumberOfPlans AS VARCHAR) + ' new coverage plans';
            END
            """)
            
            # Simulation.CreateNewPolicies
            execute_script(conn, """
            IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Simulation.CreateNewPolicies') AND type in (N'P'))
                DROP PROCEDURE Simulation.CreateNewPolicies
            """)
            execute_script(conn, """
            CREATE PROCEDURE Simulation.CreateNewPolicies
                @NumberOfPolicies INT = 10
            AS
            BEGIN
                SET NOCOUNT ON;
                
                -- This is a placeholder procedure that will be implemented in Python
                -- The Python application will create new policies for members
                -- and insert them into the Insurance.Policies table
                
                PRINT 'Creating ' + CAST(@NumberOfPolicies AS VARCHAR) + ' new policies';
            END
            """)
            
            # Simulation.DailyProcessToCreateHistory
            execute_script(conn, """
            IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Simulation.DailyProcessToCreateHistory') AND type in (N'P'))
                DROP PROCEDURE Simulation.DailyProcessToCreateHistory
            """)
            execute_script(conn, """
            CREATE PROCEDURE Simulation.DailyProcessToCreateHistory
                @SimulationDate DATE = NULL,
                @AddNewMembers BIT = 1,
                @NewMembersCount INT = 5,
                @AddNewPlans BIT = 0,
                @NewPlansCount INT = 0,
                @CreateNewPolicies BIT = 1,
                @NewPoliciesCount INT = 3,
                @UpdateMembers BIT = 1,
                @MemberUpdatePercentage DECIMAL(5,2) = 2.00,
                @ProcessPolicyChanges BIT = 1,
                @PolicyChangePercentage DECIMAL(5,2) = 1.00,
                @GenerateHospitalClaims BIT = 1,
                @HospitalClaimsCount INT = 3,
                @GenerateGeneralClaims BIT = 1,
                @GeneralClaimsCount INT = 10,
                @ProcessPremiumPayments BIT = 1,
                @ProcessClaims BIT = 1,
                @ClaimProcessPercentage DECIMAL(5,2) = 80.00
            AS
            BEGIN
                SET NOCOUNT ON;
                
                -- Use current date if no simulation date provided
                IF @SimulationDate IS NULL
                    SET @SimulationDate = GETDATE();
                
                PRINT 'Running daily simulation for ' + CONVERT(VARCHAR, @SimulationDate, 103);
                
                -- This is a placeholder procedure that will be implemented in Python
                -- The Python application will orchestrate all the daily processes
                -- based on the parameters provided
                
                PRINT 'Daily simulation completed for ' + CONVERT(VARCHAR, @SimulationDate, 103);
            END
            """)
            
            logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        return

if __name__ == '__main__':
    main()