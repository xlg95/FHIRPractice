from typing import Literal

class Patient():
    def __init__(self,
                 first_name: str,
                 last_name: str,
                 gender: Literal["male", "female", "other", "unknown"],
                 birth_date: str):
        self.first_name = first_name
        self.last_name = last_name
        if self.gender in ["male", "female", "other", "unknown"]:
            self.gender = gender
        else:
            raise ValueError("Gender must be one of these values: male/female/other/unknown")
        self.birth_date = birth_date

    def get_patient_resource(self):
        return {
            "resourceType": "Patient",
            "name": [
                {
                    "family": self.last_name,
                    "given": [n for n in self.first_name.split(" ")]
                }
            ],
            "gender": self.gender,
            "birthDate": self.birth_date
        }  
