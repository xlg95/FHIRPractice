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
    
    def create_patient(self, patient_data):
        response = requests.post(f"{self.base_url}/Patient", json=patient_data)
        return response.json()
    
    def update_patient(self, person_id, patient_data):
        response = requests.put(f"{self.base_url}/Patient/{person_id}", json=patient_data)
        return response.json()