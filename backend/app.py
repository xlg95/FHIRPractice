from fhir_client import FHIRClient, FHIR_BASE
from fhir_medication_statement_builder import FHIR_Builder_Medication_Statement
from resources.patient import Patient
from resources.medication import Medication
#from fhir.resources.patient import Patient
import json
import hl7
from hl7apy.parser import parse_message
from hl7decoder import Hl7Decoder
import random
import os
from itertools import count
from time import sleep
from datetime import datetime
from zoneinfo import ZoneInfo

hl7example_filepath = os.path.join(os.getcwd(), "backend", "data", "hl7_example.hl7")
print(hl7example_filepath)

fhir_client = FHIRClient(FHIR_BASE)
try:
    create_patient = False
    update_patient = False
    delete_patient = False
    print_patient_data = False

    create_medication = False
    delete_medication = False

    hl7ModulesCode = False
    hl7CustomDecoder = False

    build_medication_statement = True
except: pass

def update_patient_data(patient_id, entry, new_value):
    patient_data = fhir_client.get_patient_by_id(patient_id)
    patient_data[entry] = new_value
    print(patient_data)
    fhir_client.update_patient(patient_id, patient_data)

print("FHIR Playground gestartet")


if print_patient_data:
    
    #fhir_persondata = fhir_client.get_patient_by_id(1000)
    #print(fhir_persondata)
    #print(fhir_client.get_patientdata())
    for patient in fhir_client.get_patientdata()["entry"]:
        print(f"{patient['resource']}")

if create_patient:
    bm = random.randint(1,12)
    bd = random.randint(1,31 - (bm in [4,6,9,11]) - 3*(bm == 2))

    patient_ressource = Patient(
        first_name="Geraldin",
        last_name="Meier",
        gender="female",
        birth_date=f"1995-{bm:02d}-{bd:02d}"
    ).get_patient_resource()

    print(patient_ressource)

    create_patient_response = fhir_client.create_patient(patient_ressource)
    print(f"create_patient_response: {create_patient_response}")

if update_patient:
    update_patient_data(1001, "gender", "female")

    update_patient_data(1001, "name", [{'family': 'Mustermann', 'given': ['Maria']}])

if delete_patient:
    delete_patient_response = fhir_client.delete_patient(1004)
    print(delete_patient_response)

if create_medication:

    medication_resource = Medication(
        code_coding=[
                    {
                        "system": "http://fhir.de/CodeSystem/bfarm/atc",
                        "code": "N02BE01",
                        "display": "Paracetamol"
                    },
                    {
                        "system": "http://snomed.info/sct",
                        "code": "387517004",
                        "display": "Paracetamol-containing product"
                    }
                ],
        code_text="Paracetamol 500 mg Tablette",
        form_coding=[
                    {
                        "system": "http://snomed.info/sct",
                        "code": "385055001",
                        "display": "Tablet dose form"
                    }
                ],
        form_text = "Tablette",
        ingredient_itemCodableConcept_coding=[
                            {
                                "system": "http://fhir.de/CodeSystem/bfarm/atc",
                                "code": "N02BE01",
                                "display": "Paracetamol"
                            }
                        ],
        ingredient_itemCodableConcept_text="Paracetamol 500 mg Tablette",
        numerator_value=500,
        numerator_unit="mg",
        denominator_value=1,
        denominator_unit="Tablet",
        identifier = [
                {
                    "system": "https://avelios.de/medications",
                    "value": "4711"
                }
            ]
    ).get_medication_resource()

    create_medication_response = fhir_client.create_medication(medication_data=medication_resource)
    print(f"create_medication_response: {create_medication_response}")

if delete_medication:
    delete_medication_response = fhir_client.delete_medication(1013)
    print(delete_medication_response)
    delete_medication_response = fhir_client.delete_medication(1014)
    print(delete_medication_response)

if hl7ModulesCode:
    hl7str = ""
    with open(hl7example_filepath, 'r') as hl7file:
        for line in hl7file: 
            hl7str += line


    msg = parse_message(hl7str)

    print(msg)
    pid = msg.PID
    print(f"pid: {pid}")
    print(pid)
    print(pid.pid_5.pid_5_1.value)  # Nachname
    print(pid.pid_5.pid_5_2.value)  # Vorname


    #message = hl7.parse(hl7str)

    #print(message)

if hl7CustomDecoder:
    hl7decoder = None
    with open(hl7example_filepath, 'r') as hl7File:
        hl7decoder = Hl7Decoder("".join(line for line in hl7File).strip())

    #print("hl7decmsg:", hl7decoder.message)
    hl7decoder.decodeMSH()

if build_medication_statement:
    hl7decoder = None
    with open(hl7example_filepath, 'r') as hl7File:
        hl7decoder = Hl7Decoder("".join(line for line in hl7File).strip())
    hl7data = hl7decoder.decodeMessage()

    fhir_medication_statement_builder = FHIR_Builder_Medication_Statement(hl7_data=hl7data)
    fhir_medication_statement_builder.build_fhir_resource_json()


is_german_summertime= lambda: datetime.now(ZoneInfo("Europe/Berlin")).dst().total_seconds() != 0

print(is_german_summertime())