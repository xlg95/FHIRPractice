from fhir_client import FHIRClient, FHIR_BASE

print("FHIR Playground gestartet")

fhir_client = FHIRClient(FHIR_BASE)
fhir_persondata = fhir_client.get_patient_by_id(1000)
print(fhir_persondata)