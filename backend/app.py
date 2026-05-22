from fhir_client import FHIRClient, FHIR_BASE
from resources.patient import Patient
import json
create_patient = True
update_patient = False

def update_patient_data(patient_id, entry, new_value):
    patient_data = fhir_client.get_patient_by_id(patient_id)
    patient_data[entry] = new_value
    print(patient_data)
    fhir_client.update_patient(patient_id, patient_data)


print("FHIR Playground gestartet")

fhir_client = FHIRClient(FHIR_BASE)
fhir_persondata = fhir_client.get_patient_by_id(1000)
print(fhir_persondata)
print(fhir_client.get_patientdata())
for patient in fhir_client.get_patientdata()["entry"]:
    print(f"{patient['resource']}")

if create_patient:
    patient_ressource = Patient(
        first_name="Susanne",
        last_name="Schmidt",
        gender="female",
        birth_date="1981-05-21"
    ).get_patient_resource()

    print(patient_ressource)

    create_patient_response = fhir_client.create_patient(patient_ressource)
    print(create_patient_response)


if update_patient:
    update_patient_data(1001, "gender", "female")

    update_patient_data(1001, "name", [{'family': 'Mustermann', 'given': ['Maria']}])