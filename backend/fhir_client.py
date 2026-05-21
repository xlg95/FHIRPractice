import requests

FHIR_BASE = "http://localhost:8080/fhir"



class FHIRClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_metadata(self):
        response = requests.get(f"{self.base_url}/metadata")
        return response.json()
    
    def get_patientdata(self):
        response = requests.get(f"{self.base_url}/Patient")
        return response.json()
    
    def get_patient_by_id(self, person_id):
        response = requests.get(f"{self.base_url}/Patient/{person_id}")
        return response.json()