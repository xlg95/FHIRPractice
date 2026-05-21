from fhir_client import FHIRClient, FHIR_BASE
from resources.patient import create_patient_resource
import json
create_patient = False

print("FHIR Playground gestartet")

fhir_client = FHIRClient(FHIR_BASE)
fhir_persondata = fhir_client.get_patient_by_id(1000)
print(fhir_persondata)
print(fhir_client.get_patientdata())
for patient in fhir_client.get_patientdata()["entry"]:
    print(patient["resource"])

if create_patient:
    patient_ressource = create_patient_resource(
        first_name="Günther",
        last_name="Schmidt",
        gender="male",
        birth_date="1980-01-01"
    )

    print(patient_ressource)

    create_patient_response = fhir_client.create_patient(patient_ressource)
    print(create_patient_response)
