from helpers.ucum import is_valid_ucum

class Medication():
    def __init__(self,
                 code_coding: list[dict],
                 code_text: str,
                 form_coding: list[dict],
                 form_text: str,
                 ingredient_itemCodableConcept_coding: list[dict],
                 ingredient_itemCodableConcept_text: str,
                 numerator_value: int,
                 numerator_unit: str,
                 denominator_value: int,
                 denominator_unit: str,
                 profile: list[str] = ["https://www.medizininformatik-initiative.de/fhir/modul-medikation/StructureDefinition/Medication"]):
        self.profile = profile
        self.code_coding = code_coding
        self.code_text = code_text
        self.form_coding = form_coding
        self.form_text = form_text
        self.ingredient_itemCodableConcept_coding = ingredient_itemCodableConcept_coding
        self.ingredient_itemCodableConcept_text = ingredient_itemCodableConcept_text
        self.numerator_value = numerator_value
        if is_valid_ucum(numerator_unit):
            self.numerator_unit = numerator_unit
        else:
            raise ValueError("The numerator Unit must be valid UCUM")
        self.denominator_value = denominator_value
        self.denominator_unit = denominator_unit

    def get_medication_resource(self):
        # code 
        code: dict = {
                "coding": self.code_coding
            }
        if self.code_text:
            code["text"] = self.code_text

        # form
        form: dict = {
                "coding": self.form_coding
            }
        if self.form_text:
            form["text"] = self.form_text

        # itemCodeableConcept
        itemCodeableConcept: dict = {
                        "coding": self.ingredient_itemCodableConcept_coding
                    }
        if self.ingredient_itemCodableConcept_text:
            itemCodeableConcept["text"] = self.ingredient_itemCodableConcept_text

        return {
            "resourceType": "Medication",

            "meta": {
                "profile": self.profile
            },

            # Must Support
            "code": code,

            # Must Support
            "form": form,

            # Must Support
            "ingredient": [
                {
                    "itemCodeableConcept": itemCodeableConcept,

                    "strength": {
                        "numerator": {
                            "value": self.numerator_value,
                            "unit": self.numerator_unit
                        },

                        "denominator": {
                            "value": self.denominator_value,
                            "unit": self.denominator_unit
                        }
                    }
                }
            ]
        }