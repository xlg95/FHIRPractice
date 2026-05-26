from fhir_client import FHIRClient, FHIR_BASE
from resources.patient import Patient
#from fhir.resources.patient import Patient
import json

import random

print(random.randint(1,12))

create_patient = False
update_patient = False
delete_patient = False
print_patient_data = False

def update_patient_data(patient_id, entry, new_value):
    patient_data = fhir_client.get_patient_by_id(patient_id)
    patient_data[entry] = new_value
    print(patient_data)
    fhir_client.update_patient(patient_id, patient_data)

print("FHIR Playground gestartet")

if print_patient_data:
    fhir_client = FHIRClient(FHIR_BASE)
    fhir_persondata = fhir_client.get_patient_by_id(1000)
    print(fhir_persondata)
    print(fhir_client.get_patientdata())
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
    print(create_patient_response)


if update_patient:
    update_patient_data(1001, "gender", "female")

    update_patient_data(1001, "name", [{'family': 'Mustermann', 'given': ['Maria']}])

if delete_patient:
    delete_patient_response = fhir_client.delete_patient(1004)
    print(delete_patient_response)