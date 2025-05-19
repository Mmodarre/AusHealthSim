"""
Integration tests for Synthea FHIR integration.
"""
import pytest
from datetime import date, timedelta
import os
import sys
import uuid
import json
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from health_insurance_au.utils.db_utils import execute_query, execute_non_query
from health_insurance_au.integration.synthea import SyntheaIntegration


class TestSyntheaIntegration:
    """Integration tests for Synthea FHIR integration."""
    
    @pytest.fixture
    def sample_patient_data(self):
        """Create sample patient FHIR data."""
        return {
            "resourceType": "Patient",
            "id": "test-patient-id",
            "meta": {
                "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
            },
            "extension": [
                {
                    "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
                    "extension": [
                        {
                            "url": "ombCategory",
                            "valueCoding": {
                                "system": "urn:oid:2.16.840.1.113883.6.238",
                                "code": "2106-3",
                                "display": "White"
                            }
                        }
                    ]
                }
            ],
            "identifier": [
                {
                    "system": "https://github.com/synthetichealth/synthea",
                    "value": "test-patient-id"
                },
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "code": "MR",
                                "display": "Medical Record Number"
                            }
                        ]
                    },
                    "system": "http://hospital.smarthealthit.org",
                    "value": "test-patient-id"
                }
            ],
            "name": [
                {
                    "family": "TestFamily",
                    "given": ["TestGiven"]
                }
            ],
            "telecom": [
                {
                    "system": "phone",
                    "value": "555-123-4567",
                    "use": "home"
                },
                {
                    "system": "email",
                    "value": "test.patient@example.com"
                }
            ],
            "gender": "male",
            "birthDate": "1990-01-01",
            "address": [
                {
                    "line": ["123 Test Street"],
                    "city": "Sydney",
                    "state": "NSW",
                    "postalCode": "2000",
                    "country": "AU"
                }
            ],
            "maritalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                        "code": "S",
                        "display": "Single"
                    }
                ],
                "text": "Single"
            }
        }
    
    @pytest.fixture
    def sample_encounter_data(self):
        """Create sample encounter FHIR data."""
        return {
            "resourceType": "Encounter",
            "id": "test-encounter-id",
            "meta": {
                "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter"]
            },
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory"
            },
            "type": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "185345009",
                            "display": "Encounter for check up"
                        }
                    ],
                    "text": "Encounter for check up"
                }
            ],
            "subject": {
                "reference": "Patient/test-patient-id"
            },
            "participant": [
                {
                    "type": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                    "code": "PPRF",
                                    "display": "primary performer"
                                }
                            ]
                        }
                    ],
                    "period": {
                        "start": "2022-01-15T08:00:00Z",
                        "end": "2022-01-15T09:00:00Z"
                    },
                    "individual": {
                        "reference": "Practitioner/test-practitioner-id",
                        "display": "Dr. Test Doctor"
                    }
                }
            ],
            "period": {
                "start": "2022-01-15T08:00:00Z",
                "end": "2022-01-15T09:00:00Z"
            },
            "reasonCode": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "185345009",
                            "display": "Encounter for check up"
                        }
                    ]
                }
            ],
            "serviceProvider": {
                "reference": "Organization/test-organization-id",
                "display": "Test Hospital"
            }
        }
    
    @pytest.fixture
    def test_member(self):
        """Create a test member."""
        # Generate a unique member number
        member_number = f"SYN{uuid.uuid4().hex[:8].upper()}"
        
        # Insert a new member
        execute_non_query("""
        INSERT INTO Insurance.Members (
            MemberNumber, FirstName, LastName, DateOfBirth, Gender,
            Email, Phone, AddressLine1, Suburb, State, Postcode,
            MedicareNumber, LHCLoading, LastModified
        ) VALUES (
            ?, 'Synthea', 'Test', '1990-01-01', 'M',
            'synthea.test@example.com', '0400123456', '123 Synthea Street', 'Sydney', 'NSW', '2000',
            '1234567890', 0.0, GETDATE()
        )
        """, (member_number,))
        
        # Get the member ID
        member_id = execute_query(
            "SELECT MemberID FROM Insurance.Members WHERE MemberNumber = ?",
            (member_number,)
        )[0]['MemberID']
        
        yield {'member_id': member_id, 'member_number': member_number}
        
        # Clean up
        execute_non_query(
            "DELETE FROM Insurance.Members WHERE MemberNumber = ?",
            (member_number,)
        )
    
    @pytest.fixture
    def test_policy(self, test_member):
        """Create a test policy."""
        # Generate a unique policy number
        policy_number = f"SYN{uuid.uuid4().hex[:8].upper()}"
        
        # Create a test coverage plan
        plan_code = f"SYN{uuid.uuid4().hex[:8].upper()}"
        
        execute_non_query("""
        INSERT INTO Insurance.CoveragePlans (
            PlanCode, PlanName, CoverageType, HospitalTier, HospitalExcess,
            HospitalCoveragePercentage, ExtrasCoveragePercentage, MonthlyPremium,
            AnnualLimitExtras, WaitingPeriodHospital, WaitingPeriodExtras,
            WaitingPeriodPreExisting, EffectiveDate, LastModified
        ) VALUES (
            ?, 'Synthea Test Plan', 'Combined', 'Silver', 500,
            85.0, 60.0, 150.0,
            1000.0, 2, 2,
            12, GETDATE(), GETDATE()
        )
        """, (plan_code,))
        
        # Get the plan ID
        plan_id = execute_query(
            "SELECT PlanID FROM Insurance.CoveragePlans WHERE PlanCode = ?",
            (plan_code,)
        )[0]['PlanID']
        
        # Insert the policy
        execute_non_query("""
        INSERT INTO Insurance.Policies (
            PolicyNumber, PlanID, StartDate, Status, PaymentFrequency,
            PaymentMethod, LastPremiumPaidDate, NextPremiumDueDate,
            HospitalWaitingCompleted, ExtrasWaitingCompleted,
            PreExistingWaitingCompleted, LastModified
        ) VALUES (
            ?, ?, GETDATE(), 'Active', 'Monthly',
            'DirectDebit', GETDATE(), DATEADD(month, 1, GETDATE()),
            0, 0, 0, GETDATE()
        )
        """, (policy_number, plan_id))
        
        # Get the policy ID
        policy_id = execute_query(
            "SELECT PolicyID FROM Insurance.Policies WHERE PolicyNumber = ?",
            (policy_number,)
        )[0]['PolicyID']
        
        # Link member to policy
        execute_non_query("""
        INSERT INTO Insurance.PolicyMembers (
            PolicyID, MemberID, RelationshipType, IsMainMember, LastModified
        ) VALUES (
            ?, ?, 'Self', 1, GETDATE()
        )
        """, (policy_id, test_member['member_id']))
        
        yield {'policy_id': policy_id, 'policy_number': policy_number, 'plan_id': plan_id}
        
        # Clean up
        execute_non_query(
            "DELETE FROM Insurance.PolicyMembers WHERE PolicyID = ?",
            (policy_id,)
        )
        execute_non_query(
            "DELETE FROM Insurance.Policies WHERE PolicyNumber = ?",
            (policy_number,)
        )
        execute_non_query(
            "DELETE FROM Insurance.CoveragePlans WHERE PlanCode = ?",
            (plan_code,)
        )
    
    def test_import_patients(self, sample_patient_data, tmp_path):
        """Test importing Synthea patients."""
        # Create a temporary FHIR directory
        fhir_dir = tmp_path / "fhir"
        fhir_dir.mkdir()
        
        # Create a sample patient file
        patient_file = fhir_dir / "Patient_test-patient-id.json"
        with open(patient_file, 'w') as f:
            json.dump(sample_patient_data, f)
        
        # Initialize Synthea integration
        synthea = SyntheaIntegration(str(fhir_dir))
        
        # Import patients
        imported_count = synthea.import_patients()
        
        # Check that the patient was imported
        result = execute_query("""
        SELECT * FROM Integration.SyntheaPatients
        WHERE PatientFHIRID = ?
        """, (sample_patient_data['id'],))
        
        assert len(result) == 1
        assert result[0]['PatientData'] is not None
        
        # Clean up
        execute_non_query(
            "DELETE FROM Integration.SyntheaPatients WHERE PatientFHIRID = ?",
            (sample_patient_data['id'],)
        )
    
    def test_import_encounters(self, sample_patient_data, sample_encounter_data, tmp_path):
        """Test importing Synthea encounters."""
        # Create a temporary FHIR directory
        fhir_dir = tmp_path / "fhir"
        fhir_dir.mkdir()
        
        # Create sample files
        patient_file = fhir_dir / "Patient_test-patient-id.json"
        with open(patient_file, 'w') as f:
            json.dump(sample_patient_data, f)
            
        encounter_file = fhir_dir / "Encounter_test-encounter-id.json"
        with open(encounter_file, 'w') as f:
            json.dump(sample_encounter_data, f)
        
        # Initialize Synthea integration
        synthea = SyntheaIntegration(str(fhir_dir))
        
        # Import patients first
        synthea.import_patients()
        
        # Import encounters
        imported_count = synthea.import_encounters()
        
        # Check that the encounter was imported
        result = execute_query("""
        SELECT * FROM Integration.SyntheaEncounters
        WHERE EncounterFHIRID = ?
        """, (sample_encounter_data['id'],))
        
        assert len(result) == 1
        assert result[0]['PatientFHIRID'] == sample_patient_data['id']
        assert result[0]['EncounterData'] is not None
        
        # Clean up
        execute_non_query(
            "DELETE FROM Integration.SyntheaEncounters WHERE EncounterFHIRID = ?",
            (sample_encounter_data['id'],)
        )
        execute_non_query(
            "DELETE FROM Integration.SyntheaPatients WHERE PatientFHIRID = ?",
            (sample_patient_data['id'],)
        )
    
    def test_link_patients_to_members(self, sample_patient_data, test_member, tmp_path):
        """Test linking Synthea patients to members."""
        # Create a temporary FHIR directory
        fhir_dir = tmp_path / "fhir"
        fhir_dir.mkdir()
        
        # Create a sample patient file
        patient_file = fhir_dir / "Patient_test-patient-id.json"
        with open(patient_file, 'w') as f:
            json.dump(sample_patient_data, f)
        
        # Initialize Synthea integration
        synthea = SyntheaIntegration(str(fhir_dir))
        
        # Import patients
        synthea.import_patients()
        
        # Link patients to members
        linked_count = synthea.link_patients_to_members()
        
        # Check that the patient was linked
        result = execute_query("""
        SELECT * FROM Integration.SyntheaPatients
        WHERE PatientFHIRID = ?
        """, (sample_patient_data['id'],))
        
        assert len(result) == 1
        assert result[0]['MemberID'] is not None
        
        # Clean up
        execute_non_query(
            "DELETE FROM Integration.SyntheaPatients WHERE PatientFHIRID = ?",
            (sample_patient_data['id'],)
        )
    
    def test_generate_claims_from_encounters(self, sample_patient_data, sample_encounter_data, test_member, test_policy, tmp_path):
        """Test generating claims from Synthea encounters."""
        # Create a temporary FHIR directory
        fhir_dir = tmp_path / "fhir"
        fhir_dir.mkdir()
        
        # Create sample files
        patient_file = fhir_dir / "Patient_test-patient-id.json"
        with open(patient_file, 'w') as f:
            json.dump(sample_patient_data, f)
            
        encounter_file = fhir_dir / "Encounter_test-encounter-id.json"
        with open(encounter_file, 'w') as f:
            json.dump(sample_encounter_data, f)
        
        # Initialize Synthea integration
        synthea = SyntheaIntegration(str(fhir_dir))
        
        # Import patients and encounters
        synthea.import_patients()
        synthea.import_encounters()
        
        # Update the patient with the member ID
        execute_non_query("""
        UPDATE Integration.SyntheaPatients
        SET MemberID = ?
        WHERE PatientFHIRID = ?
        """, (test_member['member_id'], sample_patient_data['id']))
        
        # Generate claims from encounters
        claims_count = synthea.generate_claims_from_encounters()
        
        if claims_count > 0:
            # Check that claims were generated
            result = execute_query("""
            SELECT c.* 
            FROM Insurance.Claims c
            JOIN Integration.SyntheaEncounters e ON e.ClaimID = c.ClaimID
            WHERE e.EncounterFHIRID = ?
            """, (sample_encounter_data['id'],))
            
            assert len(result) > 0
            assert result[0]['MemberID'] == test_member['member_id']
            assert result[0]['PolicyID'] == test_policy['policy_id']
            
            # Clean up
            for row in result:
                execute_non_query(
                    "DELETE FROM Insurance.Claims WHERE ClaimID = ?",
                    (row['ClaimID'],)
                )
        
        # Clean up
        execute_non_query(
            "DELETE FROM Integration.SyntheaEncounters WHERE EncounterFHIRID = ?",
            (sample_encounter_data['id'],)
        )
        execute_non_query(
            "DELETE FROM Integration.SyntheaPatients WHERE PatientFHIRID = ?",
            (sample_patient_data['id'],)
        )