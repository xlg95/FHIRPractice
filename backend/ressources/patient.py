def create_patient_resource(
    first_name,
    last_name,
    gender,
    birth_date
):
    return {
        "resourceType": "Patient",
        "name": [
            {
                "family": last_name,
                "given": [first_name]
            }
        ],
        "gender": gender,
        "birthDate": birth_date
    }