from fhir_client import FHIRClient, FHIR_BASE

print("FHIR Playground gestartet")

fhir_client = FHIRClient(FHIR_BASE)
fhir_persondata = fhir_client.get_persondata()
print(fhir_persondata)