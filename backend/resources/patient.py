class Patient():
    def __init__(self,
                 first_name,
                 last_name,
                 gender,
                 birth_date):
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.birth_date = birth_date

    def get_patient_resource(self):
        return {
            "resourceType": "Patient",
            "name": [
                {
                    "family": self.last_name,
                    "given": [self.first_name]
                }
            ],
            "gender": self.gender,
            "birthDate": self.birth_date
        }  
