from hl7_data import HL7Data
import base64
import xml.etree.ElementTree as ET
from uuid import UUID
from datetime import datetime
from zoneinfo import ZoneInfo
from mappings.Dosiereinheit import DOSIEREINHEIT, BMP_TO_FHIR_QUANTITY_UNIT
from mappings.EventTiming import EVENT_TIMING, BMP_KEY_TO_EVENT
import json

def is_valid_uuid(uuid: str) -> bool:
    try:
        return bool(UUID(uuid))
    except (ValueError, TypeError) as error:
        return False

def is_valid_pzn(pzn: str):
    num_list = ([0]*(8-len(pzn)))+[int(x) for x in str(pzn)[:len(pzn)-1]]
    r = sum(x*(i+1) for i,x in enumerate(num_list))
    return r%11 == int(pzn)%10

is_german_summertime= lambda: datetime.now(ZoneInfo("Europe/Berlin")).dst().total_seconds() != 0 # TODO: DOES THIS MAKE SENSE AT ALL?

class FHIR_Builder_Medication_Statement:
    def __init__(self, hl7_data: HL7Data):
        self.hl7_data: HL7Data = hl7_data
        self.xml_decoded = None
        self.RESOURCE_NAME = "MedicationStatement"

    def build_fhir_resource_json(self):
        medicationplan_UUID, medicament_pzn_list = self.get_medicationplan_ids()
        if not is_valid_uuid(medicationplan_UUID):
            print(f"The UUID {medicationplan_UUID} is invalid.. please check")

        fhir_resource_list = list()
        for i, medicament_pzn in enumerate(medicament_pzn_list):

            # resourceType
            json_dict = {"resourceType": f"{self.RESOURCE_NAME}"}

            # id
            #json_dict["id"] = f"{medicationplan_UUID}-{medicament_pzn}"

            # meta.source
            hl7_version = f"hl7v{self.hl7_data.msh_segment.version_id}"
            message_type = f"{self.hl7_data.msh_segment.message_type.split("^")[0]}_{self.hl7_data.msh_segment.message_type.split("^")[1]}"
            json_dict["meta"] = dict()
            json_dict["meta"]["source"] = f"urn:{hl7_version}:{message_type}:{self.hl7_data.msh_segment.message_control_id}"
            json_dict["meta"]["profile"] = f"https://www.medizininformatik-initiative.de/fhir/core/modul-medikation/StructureDefinition/{self.RESOURCE_NAME}"

            # identifier.system and identifier.value
            json_dict["identifier"] = list()
            json_dict["identifier"].append({"system": "urn:bmp", "value": f"{medicationplan_UUID}"})    # TODO: CHECK MF

            # status
            json_dict["status"] = "active"  #TODO: HOW DO I KNOW IT IS ACTIVE? WHAT ELSE CAN IT BE?

            # medicationCodeableConcept
            json_dict["medicationCodeableConcept"] = dict()
            json_dict["medicationCodeableConcept"]["coding"] = list()
            #json_dict["medicationCodeableConcept"]["text"] = f"PZN {medicament_pzn}"
            medicationCodableConcept_coding = {"system": "http://fhir.de/CodeSystem/ifa/pzn", "code": f"{medicament_pzn}", "display": f"PZN {medicament_pzn}"}
            json_dict["medicationCodeableConcept"]["coding"].append(medicationCodableConcept_coding)

            # subject
            json_dict["subject"] = dict()
            json_dict["subject"]["reference"] = f"Patient/{self.hl7_data.pid_segment.patient_id}"
            json_dict["subject"]["display"] = f"{self.get_name()}"

            # context
            json_dict["context"] = dict()
            json_dict["context"]["reference"] = f"Encounter/{self.hl7_data.pv1_segment.visit_number}" #TODO: Check if we can do this

            # effectiveDateTime
            effectiveDateTime = self.get_effective_datetime()
            json_dict["effectiveDateTime"] = f"{effectiveDateTime}"  #TODO: CHECK

            # dateAsserted
            #json_dict["dateAsserted"] = f"{effectiveDateTime}"  #TODO: CHECK

            # informationSource  # TODO: CHECK THIS.. HAS TO BE A REFERENCE AND NOT A STRING
            #json_dict["informationSource"] = dict()
            #json_dict["informationSource"]["display"] = f"{self.get_informationSource_display()}"

            # dosage
            dosage_values = self.get_dosage_values_by_pzn(medicament_pzn)
            
            dosage_unit_code = dosage_values.get("du")
            json_dict["dosage"] = list()

            when: dict[str, int|float] = dict()
            for key, value in dosage_values.items():
                if key in BMP_KEY_TO_EVENT:
                    when[BMP_KEY_TO_EVENT[key]] = numerical(value)

            when_inverted: dict[int|float, list[str]] = {}
            for k, v in when.items():
                when_inverted.setdefault(v, []).append(k)            
            
            for amount, event_keys in when_inverted.items():
                dosage_entry = dict()
                text: str = f"{amount} {DOSIEREINHEIT[dosage_unit_code]} {' und '.join(EVENT_TIMING[event_key][2] for event_key in event_keys)}"
                dosage_entry["text"] = text
                dosage_entry["timing"] = dict()
                dosage_entry["timing"]["repeat"] = dict()
                dosage_entry["timing"]["repeat"]["when"] = event_keys
                dosage_entry["doseAndRate"] = list()
                dose_and_rate_entry = dict()
                dose_and_rate_entry["doseQuantity"] = dict()
                dose_and_rate_entry["doseQuantity"]["value"] = amount
                dose_and_rate_entry["doseQuantity"]["unit"] = BMP_TO_FHIR_QUANTITY_UNIT[dosage_unit_code]["unit"]
                if BMP_TO_FHIR_QUANTITY_UNIT[dosage_unit_code]["system"]:
                    dose_and_rate_entry["doseQuantity"]["system"] = BMP_TO_FHIR_QUANTITY_UNIT[dosage_unit_code]["system"]
                if BMP_TO_FHIR_QUANTITY_UNIT[dosage_unit_code]["code"]:
                    dose_and_rate_entry["doseQuantity"]["code"] = BMP_TO_FHIR_QUANTITY_UNIT[dosage_unit_code]["code"]
                dosage_entry["doseAndRate"].append(dose_and_rate_entry)
                json_dict["dosage"].append(dosage_entry)
            
            # append
            fhir_resource_list.append(json_dict)
        for i, fhir_resource in enumerate(fhir_resource_list):
            #print(f"{i:2d}: {fhir_resource}")

            with open(f'C:\\Users\\Alexander\\Documents\\TBD\\result_{i:03d}.json', 'w') as json_file:
                json.dump(fhir_resource, json_file)

    def decodexml(self):
        # TODO: maybe check the other OBX Segments for "XML-Dokument Bundesmedikationsplan" and "Entlass", etc.
        encoded_xml = next(obx_segment.observation_value.split("^")[4] for obx_segment in self.hl7_data.obx_segment_list if obx_segment.observation_value.split("^")[3] == "BASE64")
        decoded_xml = base64.b64decode(encoded_xml + '=' * (-len(encoded_xml) % 4))
        self.xml_decoded = decoded_xml

    def get_medicationplan_ids(self) -> tuple[str, list[str]]:
        medicationplan_UUID, medicament_pzn_list = None, list()
        if self.xml_decoded == None:
            self.decodexml()
        root = ET.fromstring(self.xml_decoded)

        # Attribut U aus dem MP-Element
        u = root.get("U")
        medicationplan_UUID = u

        # Alle p-Attribute aus den M-Elementen innerhalb von S
        for m in root.findall("./S/M"):
            pzn = m.get("p")
            if is_valid_pzn(pzn):
                medicament_pzn_list.append(pzn)
            else:
                print(f"Invalid PZN ({pzn}) was found in the medication Plan")
        return (medicationplan_UUID, medicament_pzn_list)
    
    def get_dosage_values_by_pzn(self, pzn):
                if self.xml_decoded == None:
                    self.decodexml()
                root = ET.fromstring(self.xml_decoded)
                for m in root.findall(".//M"):
                    if m.get("p") == str(pzn):
                        return m.attrib   # 👈 ALLE Attribute dynamisch
                return None

    def get_name(self) -> str:
        if self.xml_decoded == None:
            self.decodexml()
        root = ET.fromstring(self.xml_decoded)
        p = root.find("P")
        return f"{p.get("g")} {p.get("f")}"
    
    def get_informationSource_display(self) -> str:
        if self.xml_decoded == None:
            self.decodexml()
        root = ET.fromstring(self.xml_decoded)
        a = root.find("A")
        return f"{a.get("n")}"
        
    def get_effective_datetime(self) -> str:
        if self.xml_decoded == None:
            self.decodexml()
        root = ET.fromstring(self.xml_decoded)
        a = root.find("A")
        dt = a.get("t")
        return f"{dt}"
        return f"{dt}+{(1+is_german_summertime()):02d}:00" # KÖNNTE GENUTZT WERDEN FALLS ZEITDATEN IM BMP UTC SIND (UNWAHRSCHEINLICH)
    
    def get_derived_from(self) -> str:
        if self.xml_decoded == None:
            self.decodexml()
        root = ET.fromstring(self.xml_decoded)
        v = root.get("v")
        return f"Bundesmedikationsplan Version {v}"
    
def numerical(v):
    if v is None:
        return None

    if isinstance(v, (int, float)):
        return v

    v = str(v).strip()
    v = v.replace(",", ".")

    try:
        f = float(v)
        return int(f) if f.is_integer() else f
    except ValueError:
        return None