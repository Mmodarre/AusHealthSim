"""
Synthea integration for the Health Insurance AU simulation.
"""
import json
import logging
import os
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from health_insurance_au.utils.db_utils import execute_query, execute_non_query, bulk_insert
from health_insurance_au.models.models import Member, Claim

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SyntheaIntegration:
    """
    Class for integrating Synthea FHIR data with the health insurance simulation.
    """
    
    def __init__(self, fhir_directory: str = None):
        """
        Initialize the Synthea integration.
        
        Args:
            fhir_directory: Directory containing Synthea FHIR JSON files
        """
        self.fhir_directory = fhir_directory
    
    def import_patients(self, limit: int = None) -> int:
        """
        Import Synthea patient data into the database.
        
        Args:
            limit: Optional limit on the number of patients to import
            
        Returns:
            Number of patients imported
        """
        if not self.fhir_directory or not os.path.exists(self.fhir_directory):
            logger.error(f"FHIR directory not found: {self.fhir_directory}")
            return 0
        
        # Find patient files
        patient_files = []
        for file in os.listdir(self.fhir_directory):
            if file.endswith('.json') and 'Patient' in file:
                patient_files.append(os.path.join(self.fhir_directory, file))
        
        if limit:
            patient_files = patient_files[:limit]
        
        logger.info(f"Found {len(patient_files)} Synthea patient files")
        
        # Process each patient file
        imported_count = 0
        for file_path in patient_files:
            try:
                with open(file_path, 'r') as f:
                    patient_data = json.load(f)
                
                # Extract patient FHIR ID
                patient_id = patient_data.get('id')
                if not patient_id:
                    logger.warning(f"No patient ID found in {file_path}")
                    continue
                
                # Store the patient data
                try:
                    query = """
                    INSERT INTO Integration.SyntheaPatients (PatientFHIRID, PatientData)
                    VALUES (?, ?)
                    """
                    execute_non_query(query, (patient_id, json.dumps(patient_data)))
                    imported_count += 1
                except Exception as e:
                    logger.error(f"Error importing patient {patient_id}: {e}")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
        
        logger.info(f"Imported {imported_count} Synthea patients")
        return imported_count
    
    def import_encounters(self, limit: int = None) -> int:
        """
        Import Synthea encounter data into the database.
        
        Args:
            limit: Optional limit on the number of encounters to import
            
        Returns:
            Number of encounters imported
        """
        if not self.fhir_directory or not os.path.exists(self.fhir_directory):
            logger.error(f"FHIR directory not found: {self.fhir_directory}")
            return 0
        
        # Find encounter files
        encounter_files = []
        for file in os.listdir(self.fhir_directory):
            if file.endswith('.json') and 'Encounter' in file:
                encounter_files.append(os.path.join(self.fhir_directory, file))
        
        if limit:
            encounter_files = encounter_files[:limit]
        
        logger.info(f"Found {len(encounter_files)} Synthea encounter files")
        
        # Process each encounter file
        imported_count = 0
        for file_path in encounter_files:
            try:
                with open(file_path, 'r') as f:
                    encounter_data = json.load(f)
                
                # Extract encounter FHIR ID
                encounter_id = encounter_data.get('id')
                if not encounter_id:
                    logger.warning(f"No encounter ID found in {file_path}")
                    continue
                
                # Extract patient reference
                patient_ref = None
                subject = encounter_data.get('subject')
                if subject and 'reference' in subject:
                    patient_ref = subject['reference'].replace('Patient/', '')
                
                if not patient_ref:
                    logger.warning(f"No patient reference found in encounter {encounter_id}")
                    continue
                
                # Store the encounter data
                try:
                    query = """
                    INSERT INTO Integration.SyntheaEncounters (EncounterFHIRID, PatientFHIRID, EncounterData)
                    VALUES (?, ?, ?)
                    """
                    execute_non_query(query, (encounter_id, patient_ref, json.dumps(encounter_data)))
                    imported_count += 1
                except Exception as e:
                    logger.error(f"Error importing encounter {encounter_id}: {e}")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
        
        logger.info(f"Imported {imported_count} Synthea encounters")
        return imported_count
    
    def import_procedures(self, limit: int = None) -> int:
        """
        Import Synthea procedure data into the database.
        
        Args:
            limit: Optional limit on the number of procedures to import
            
        Returns:
            Number of procedures imported
        """
        if not self.fhir_directory or not os.path.exists(self.fhir_directory):
            logger.error(f"FHIR directory not found: {self.fhir_directory}")
            return 0
        
        # Find procedure files
        procedure_files = []
        for file in os.listdir(self.fhir_directory):
            if file.endswith('.json') and 'Procedure' in file:
                procedure_files.append(os.path.join(self.fhir_directory, file))
        
        if limit:
            procedure_files = procedure_files[:limit]
        
        logger.info(f"Found {len(procedure_files)} Synthea procedure files")
        
        # Process each procedure file
        imported_count = 0
        for file_path in procedure_files:
            try:
                with open(file_path, 'r') as f:
                    procedure_data = json.load(f)
                
                # Extract procedure FHIR ID
                procedure_id = procedure_data.get('id')
                if not procedure_id:
                    logger.warning(f"No procedure ID found in {file_path}")
                    continue
                
                # Extract patient reference
                patient_ref = None
                subject = procedure_data.get('subject')
                if subject and 'reference' in subject:
                    patient_ref = subject['reference'].replace('Patient/', '')
                
                if not patient_ref:
                    logger.warning(f"No patient reference found in procedure {procedure_id}")
                    continue
                
                # Extract encounter reference
                encounter_ref = None
                encounter = procedure_data.get('encounter')
                if encounter and 'reference' in encounter:
                    encounter_ref = encounter['reference'].replace('Encounter/', '')
                
                if not encounter_ref:
                    logger.warning(f"No encounter reference found in procedure {procedure_id}")
                    continue
                
                # Store the procedure data
                try:
                    query = """
                    INSERT INTO Integration.SyntheaProcedures (ProcedureFHIRID, PatientFHIRID, EncounterFHIRID, ProcedureData)
                    VALUES (?, ?, ?, ?)
                    """
                    execute_non_query(query, (procedure_id, patient_ref, encounter_ref, json.dumps(procedure_data)))
                    imported_count += 1
                except Exception as e:
                    logger.error(f"Error importing procedure {procedure_id}: {e}")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
        
        logger.info(f"Imported {imported_count} Synthea procedures")
        return imported_count
    
    def link_patients_to_members(self) -> int:
        """
        Link Synthea patients to insurance members.
        
        Returns:
            Number of patients linked
        """
        logger.info("Linking Synthea patients to insurance members...")
        
        # Get unlinked Synthea patients
        unlinked_patients = execute_query("""
            SELECT SyntheaPatientID, PatientFHIRID, PatientData
            FROM Integration.SyntheaPatients
            WHERE MemberID IS NULL
        """)
        
        if not unlinked_patients:
            logger.info("No unlinked Synthea patients found")
            return 0
        
        logger.info(f"Found {len(unlinked_patients)} unlinked Synthea patients")
        
        # Get available members
        members = execute_query("""
            SELECT m.MemberID, m.FirstName, m.LastName, m.DateOfBirth, m.Gender
            FROM Insurance.Members m
            LEFT JOIN Integration.SyntheaPatients sp ON m.MemberID = sp.MemberID
            WHERE sp.MemberID IS NULL
        """)
        
        if not members:
            logger.warning("No available members found for linking")
            return 0
        
        logger.info(f"Found {len(members)} available members for linking")
        
        # Link patients to members based on matching criteria
        linked_count = 0
        for patient in unlinked_patients:
            try:
                # Parse patient data
                patient_data = json.loads(patient['PatientData'])
                
                # Extract patient details
                patient_gender = None
                if 'gender' in patient_data:
                    patient_gender = patient_data['gender'].capitalize()
                
                patient_dob = None
                if 'birthDate' in patient_data:
                    patient_dob = patient_data['birthDate']
                
                # Find matching members
                matching_members = []
                for member in members:
                    # Check gender match
                    gender_match = (
                        not patient_gender or 
                        not member['Gender'] or 
                        patient_gender == member['Gender']
                    )
                    
                    # Check approximate DOB match
                    dob_match = False
                    if patient_dob and member['DateOfBirth']:
                        try:
                            patient_date = datetime.strptime(patient_dob, '%Y-%m-%d').date()
                            member_date = member['DateOfBirth']
                            # Allow for a 5-year difference
                            dob_match = abs((patient_date - member_date).days) < 365 * 5
                        except:
                            pass
                    
                    if gender_match and (dob_match or not patient_dob or not member['DateOfBirth']):
                        matching_members.append(member)
                
                if matching_members:
                    # Select a random matching member
                    selected_member = random.choice(matching_members)
                    
                    # Link the patient to the member
                    query = """
                    UPDATE Integration.SyntheaPatients
                    SET MemberID = ?
                    WHERE SyntheaPatientID = ?
                    """
                    execute_non_query(query, (selected_member['MemberID'], patient['SyntheaPatientID']))
                    
                    # Remove the member from the available list
                    members.remove(selected_member)
                    
                    linked_count += 1
            except Exception as e:
                logger.error(f"Error linking patient {patient['PatientFHIRID']}: {e}")
                
            # Stop if we run out of available members
            if not members:
                logger.info("No more available members for linking")
                break
        
        logger.info(f"Linked {linked_count} Synthea patients to insurance members")
        return linked_count
    
    def generate_claims_from_encounters(self, limit: int = None) -> int:
        """
        Generate insurance claims from Synthea encounters.
        
        Args:
            limit: Optional limit on the number of claims to generate
            
        Returns:
            Number of claims generated
        """
        logger.info("Generating claims from Synthea encounters...")
        
        # Get encounters that don't already have claims
        encounters = execute_query("""
            SELECT e.SyntheaEncounterID, e.EncounterFHIRID, e.PatientFHIRID, e.EncounterData,
                   p.MemberID, m.FirstName, m.LastName
            FROM Integration.SyntheaEncounters e
            JOIN Integration.SyntheaPatients p ON e.PatientFHIRID = p.PatientFHIRID
            JOIN Insurance.Members m ON p.MemberID = m.MemberID
            LEFT JOIN Integration.SyntheaProcedures pr ON e.EncounterFHIRID = pr.EncounterFHIRID
            WHERE e.ClaimID IS NULL
            ORDER BY NEWID()
        """)
        
        if not encounters:
            logger.info("No eligible encounters found for claim generation")
            return 0
        
        logger.info(f"Found {len(encounters)} eligible encounters for claim generation")
        
        if limit:
            encounters = encounters[:limit]
        
        # Get policies for members
        policies = execute_query("""
            SELECT p.PolicyID, p.PolicyNumber, p.PrimaryMemberID, p.ExcessAmount, p.Status
            FROM Insurance.Policies p
            WHERE p.Status = 'Active'
        """)
        
        if not policies:
            logger.warning("No active policies found")
            return 0
        
        # Create a mapping of member ID to policy ID
        member_policy_map = {}
        for policy in policies:
            member_policy_map[policy['PrimaryMemberID']] = policy
        
        # Get providers
        providers = execute_query("""
            SELECT ProviderID, ProviderName, ProviderType
            FROM Insurance.Providers
            WHERE ProviderType IN ('Hospital', 'General Practitioner', 'Specialist')
        """)
        
        if not providers:
            logger.warning("No suitable providers found")
            return 0
        
        # Generate claims
        claims_data = []
        for encounter in encounters:
            try:
                # Check if member has an active policy
                if encounter['MemberID'] not in member_policy_map:
                    logger.debug(f"No active policy found for member {encounter['MemberID']}")
                    continue
                
                policy = member_policy_map[encounter['MemberID']]
                
                # Parse encounter data
                encounter_data = json.loads(encounter['EncounterData'])
                
                # Determine encounter type and select appropriate provider
                encounter_type = 'Hospital'
                if 'class' in encounter_data:
                    class_code = encounter_data['class'].get('code', '').lower()
                    if 'ambulatory' in class_code or 'outpatient' in class_code:
                        encounter_type = 'General Practitioner'
                    elif 'emergency' in class_code:
                        encounter_type = 'Specialist'
                
                matching_providers = [p for p in providers if p['ProviderType'] == encounter_type]
                if not matching_providers:
                    matching_providers = providers
                
                provider = random.choice(matching_providers)
                
                # Extract service date
                service_date = date.today() - timedelta(days=random.randint(1, 365))
                if 'period' in encounter_data and 'start' in encounter_data['period']:
                    try:
                        service_date = datetime.strptime(encounter_data['period']['start'], '%Y-%m-%dT%H:%M:%S%z').date()
                    except:
                        pass
                
                # Generate submission date (a few days after service date)
                submission_date = service_date + timedelta(days=random.randint(1, 10))
                
                # Extract reason for visit
                service_description = "Medical consultation"
                if 'reasonCode' in encounter_data and encounter_data['reasonCode']:
                    for reason in encounter_data['reasonCode']:
                        if 'text' in reason:
                            service_description = reason['text']
                            break
                
                # Calculate charges
                if encounter_type == 'Hospital':
                    charged_amount = round(random.uniform(500, 5000), 2)
                    medicare_amount = round(charged_amount * 0.75, 2)
                    excess_applied = min(policy['ExcessAmount'], charged_amount - medicare_amount)
                else:
                    charged_amount = round(random.uniform(80, 300), 2)
                    medicare_amount = round(charged_amount * 0.85, 2)
                    excess_applied = 0
                
                insurance_amount = round(charged_amount - medicare_amount - excess_applied, 2)
                gap_amount = max(0, round(charged_amount - medicare_amount - insurance_amount - excess_applied, 2))
                
                # Generate claim
                claim = {
                    'ClaimNumber': f"CL-{date.today().strftime('%Y%m%d')}-{random.randint(10000, 99999)}",
                    'PolicyID': policy['PolicyID'],
                    'MemberID': encounter['MemberID'],
                    'ProviderID': provider['ProviderID'],
                    'ServiceDate': service_date,
                    'SubmissionDate': submission_date,
                    'ClaimType': encounter_type,
                    'ServiceDescription': service_description,
                    'MBSItemNumber': None,
                    'ChargedAmount': charged_amount,
                    'MedicareAmount': medicare_amount,
                    'InsuranceAmount': insurance_amount,
                    'GapAmount': gap_amount,
                    'ExcessApplied': excess_applied,
                    'Status': 'Submitted',
                    'ProcessedDate': None,
                    'PaymentDate': None,
                    'RejectionReason': None
                }
                
                claims_data.append(claim)
            except Exception as e:
                logger.error(f"Error generating claim for encounter {encounter['EncounterFHIRID']}: {e}")
        
        # Insert claims into database
        if claims_data:
            try:
                rows_affected = bulk_insert("Insurance.Claims", claims_data)
                logger.info(f"Added {rows_affected} new claims from Synthea encounters")
                
                # Update encounters with claim IDs
                # This would require getting the new claim IDs and updating the encounters
                # For simplicity, we'll just mark all processed encounters as having claims
                for encounter in encounters:
                    query = """
                    UPDATE Integration.SyntheaEncounters
                    SET ClaimID = -1  # Placeholder to indicate it has been processed
                    WHERE SyntheaEncounterID = ?
                    """
                    execute_non_query(query, (encounter['SyntheaEncounterID'],))
                
                return rows_affected
            except Exception as e:
                logger.error(f"Error adding claims to database: {e}")
        
        return 0