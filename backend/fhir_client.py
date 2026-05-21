import requests

FHIR_BASE = "http://localhost:8080/fhir"



class FHIRClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_metadata(self):
        response = requests.get(f"{self.base_url}/metadata")
        return response.json()
    
    def get_persondata(self):
        response = requests.get(f"{self.base_url}/Person")
        return response.json()