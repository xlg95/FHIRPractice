from dataclasses import dataclass
from datetime import datetime

class Hl7Decoder:
    """
    @brief HL7-Message Decoder für Nachrichten vom Typ MDM_T02

    Diese Klasse verarbeitet HL7-Nachricht vom Typ MDM_T02 und gibt die Daten in aufgeschlüsselter Form zurück

    @author Alexander Gruber
    """
    def __init__(self, message: str, validate: bool=True):
        """
        @brief Initialisiert den HL7-Decoder

        Die Methode initialisiert den HL7-Decoder für Nachrichten vom Typ MDM_T02. dabei kann auch direkt die Validierung gestartet werden.
        
        @param message Die unverarbeitete HL7 Nachricht
        @param validate Angabe ob die Nachricht bei Erzeugung des HL7-Decoders automatisch validiert werden soll
        """
        self.message = message
        if validate and self.__validateMessage():
            print("Message validated")
        self.MSH_decoded_data: MSH_Data = None
        self.SFT_decoded_data: SFT_Data = None
        self.EVN_decoded_data: EVN_Data = None
        self.PID_decoded_data: PID_Data = None
        self.PV1_decoded_data: PV1_Data = None
        self.TXA_decoded_data: TXA_Data = None
        self.OBX_decoded_data_list: OBX_Data_List = OBX_Data_List

    def __validateMessage(self) -> bool:
        """
        @brief Validiert die übergebene Nachricht

        Die Methode überprüft die Nachricht auf Vollständigkeit und Fehlerfreiheit auf Basis der für Config für HL7-Nachrichten vom Typ MDM_T02
        """
        try:
            MSHSegment = next(segment for segment in self.message.split("\n") if segment.startswith("MSH"))
            MessageType = MSHSegment.split("|")[8]
            MessageCode = MessageType.split("^")[0]
            TriggerEvent = MessageType.split("^")[1]
            print(MessageType)
        except:
            raise Exception("Es wurde kein Messageheader gefunden! Bitte überprüfen Sie die HL7-Nachricht")
        if f"{MessageCode}_{TriggerEvent}" != "MDM_T02":
            raise Exception(f"Derzeit können nur HL7-Nachrichten vom Typ MDM_T02 validiert und korrekte Dekodierung garantiert werden. Ihre Nachricht ist vom Typ {MessageCode}_{TriggerEvent}. Bitte wenden Sie sich an den Entwickler Ihres Vertrauens!")
        else:
            neededSegments = {"MSH": {"numberNeeded": [1],   "name": "Message Header"},
                              "SFT": {"numberNeeded": [0,1], "name": "Software Information"},
                              "EVN": {"numberNeeded": [1],   "name": "Event Information"},
                              "PID": {"numberNeeded": [1],   "name": "Patient Information"},
                              "PV1": {"numberNeeded": [0,1], "name": "Patient Visit"},
                              "TXA": {"numberNeeded": [1],   "name": "Transcription Document Header"},
                              "OBX": {"name": "Observation Result"}} # TODO: In config File auslagern!!!
            for neededSegment, segmentData in neededSegments.items():
                if "numberNeeded" in segmentData:
                    if (numberFieldSegments:= sum(1 for segment in self.message.split("\n") if segment.startswith(neededSegment))) not in segmentData["numberNeeded"]:
                        raise Exception(f"Es wurden {numberFieldSegments} {segmentData["name"]} Segmente gefunden! Die erforderliche Anzahl ist: {segmentData}! Bitte überprüfen Sie die HL7-Nachricht")
                    
            wrongSegments = [segment[:3] for segment in self.message.split("\n") if segment[:3] not in neededSegments]
            if wrongSegments:
                raise Exception(f"Es wurde mindestens ein Feld gefunden, welches nicht in eine MDM_T02 HL7 Nachricht gehört! Falsche Felder: {wrongSegments}")
            return True
                
    def get_encoding_characters_from_message(self):
        return next(segment for segment in self.message.split("\n") if segment.startswith("MSH")).split("|")[1]

    def decodeMessage(self) -> "HL7Data":
        self.decodeMSH()
        self.decodeSFT()
        self.decodeEVN()
        self.decodePID()
        self.decodePV1()
        self.decodeTXA()
        self.decodeOBX_List()
        return HL7Data(self.MSH_decoded_data, self.SFT_decoded_data, self.EVN_decoded_data, self.PID_decoded_data, self.PV1_decoded_data, self.TXA_decoded_data, self.OBX_decoded_data_list)

    def decodeMSH(self): #TODO: No config used here, just fits the MDM_T02 config
        segment = next(s for s in self.message.split("\n") if s.startswith("MSH"))
        msh_decoder = Hl7MSHDecoder(segment)
        self.MSH_decoded_data = msh_decoder.decode_segment()

    def decodeSFT(self): #TODO
        encoding_characters = self.MSH_decoded_data.encoding_characters or self.get_encoding_characters_from_message()
        segment = next((s for s in self.message.split("\n") if s.startswith("SFT")), None)
        if segment:
            sft_decoder = Hl7SFTDecoder(segment, encoding_characters)
            self.SFT_decoded_data = sft_decoder.decode_segment()

    def decodeEVN(self):
        encoding_characters = self.MSH_decoded_data.encoding_characters or self.get_encoding_characters_from_message()
        segment = next(s for s in self.message.split("\n") if s.startswith("EVN"))
        evn_decoder = Hl7EVNDecoder(segment, encoding_characters)
        self.EVN_decoded_data = evn_decoder.decode_segment()

    def decodePID(self):
        encoding_characters = self.MSH_decoded_data.encoding_characters or self.get_encoding_characters_from_message()
        segment = next(s for s in self.message.split("\n") if s.startswith("PID"))
        pid_decoder = Hl7PIDDecoder(segment, encoding_characters)
        self.PID_decoded_data = pid_decoder.decode_segment()

    def decodePV1(self):
        encoding_characters = self.MSH_decoded_data.encoding_characters or self.get_encoding_characters_from_message()
        segment = next((s for s in self.message.split("\n") if s.startswith("PV1")), None)
        if segment:
            pv1_decoder = Hl7PV1Decoder(segment, encoding_characters)
            self.PV1_decoded_data = pv1_decoder.decode_segment()

    def decodeTXA(self):
        encoding_characters = self.MSH_decoded_data.encoding_characters or self.get_encoding_characters_from_message()
        segment = next(s for s in self.message.split("\n") if s.startswith("TXA"))
        txa_decoder = Hl7TXADecoder(segment, encoding_characters)
        self.TXA_decoded_data = txa_decoder.decode_segment()

    def decodeOBX_List(self):
        encoding_characters = self.MSH_decoded_data.encoding_characters or self.get_encoding_characters_from_message()
        for segment in [s for s in self.message.split("\n") if s.startswith("OBX")]:
            obx_decoder = Hl7OBXDecoder(segment, encoding_characters)
            self.OBX_decoded_data_list.append(obx_decoder.decode_segment())




# TODO: DIe Decoder sind alle sehr ähnlich.. maybe parent Klasse bauen und die Decoder alle davon ableiten

@dataclass
class MSH_Data:
    field_separator: str
    encoding_characters: str
    sending_application: str
    sending_facility: str
    receiving_application: str
    receiving_facility: str
    datetime_of_message: datetime
    security: str | None
    message_type: str
    message_control_id: str
    processing_id: str
    version_id: str

class Hl7MSHDecoder:
    def __init__(self, MSH_Segment):
        self.MSH_Segment = MSH_Segment
        self.field_separator = MSH_Segment[3]
        self.encoding_characters = None

    def decode_segment(self) -> MSH_Data:
        msh_fields = get_segment_fields(self.MSH_Segment, self.field_separator)
        self.encoding_characters = msh_fields[1] #TODO: Find out how to encode strings with encoding_characters better
        if any(field != '' for field in msh_fields[12:]):
            print(f"Warnung: das Message Header Segment enthält weitere Felder die noch nicht vom Decoder abgedeckt wurden")
        return MSH_Data(self.field_separator, self.encoding_characters, msh_fields[2], msh_fields[3], msh_fields[4], 
                           msh_fields[5], str_to_datetime(msh_fields[6]), msh_fields[7], msh_fields[8], msh_fields[9], msh_fields[10], msh_fields[11])

@dataclass
class SFT_Data:
    software_vendor_organization: str
    software_certified_version_or_release_number: str
    software_product_name: str
    software_binary_id: str
    software_product_information: str | None
    software_install_date: datetime | None

class Hl7SFTDecoder: 
    def __init__(self, SFT_Segment, encoding_characters):
        self.SFT_Segment = SFT_Segment
        self.field_separator = SFT_Segment[3]
        self.encoding_characters = encoding_characters #TODO: Find out how to encode strings with encoding_characters better

    def decode_segment(self)->SFT_Data:
        sft_fields = get_segment_fields(self.SFT_Segment, self.field_separator)
        if any(field != '' for i, field in enumerate(sft_fields) if i not in [1,2,3,4,5,6]):
            print(f"Warnung: das Software Information Segment enthält weitere Felder die noch nicht vom Decoder abgedeckt wurden")
        return SFT_Data(sft_fields[1], sft_fields[2], sft_fields[3], sft_fields[4], sft_fields[5], str_to_datetime(sft_fields[6]))

@dataclass
class EVN_Data:
    event_type_code: str
    recorded_datetime: str
    datetime_planned_event: str
    event_reason_code: str
    operator_id: str
    event_occurred: str
    event_facility: str

class Hl7EVNDecoder: 
    def __init__(self, EVN_Segment, encoding_characters):
        self.EVN_Segment = EVN_Segment
        self.field_separator = EVN_Segment[3]
        self.encoding_characters = encoding_characters

    def decode_segment(self) -> EVN_Data:
        evn_fields = get_segment_fields(self.EVN_Segment, self.field_separator)
        if any(field != '' for i, field in enumerate(evn_fields) if i not in [1,2,3,4,5,6,7]):
            print(f"Warnung: das Event Information Segment enthält weitere Felder die noch nicht vom Decoder abgedeckt wurden")
        return EVN_Data(evn_fields[1], evn_fields[2], evn_fields[3], evn_fields[4], evn_fields[5], evn_fields[6], evn_fields[7])

@dataclass
class PID_Data:
    set_id: str
    patient_id: str
    patient_id_list: str
    patient_name: str
    birthdate: str
    gender: str
    address: str
    phonenumber: str
    primary_language: str
    marital_status: str
    social_security_number: str
    patient_account_number: str

class Hl7PIDDecoder:
    def __init__(self, PID_Segment, encoding_characters):
        self.PID_Segment = PID_Segment
        self.field_separator = PID_Segment[3]
        self.encoding_characters = encoding_characters

    def decode_segment(self) -> PID_Data:
        pid_fields = get_segment_fields(self.PID_Segment, self.field_separator)
        if any(field != '' for i, field in enumerate(pid_fields) if i not in [1,2,3,5,7,8,11,13,15,16,18,19]):
            print(f"Warnung: das Patient Information Segment enthält weitere Felder die noch nicht vom Decoder abgedeckt wurden")
        return PID_Data(pid_fields[1], pid_fields[2], pid_fields[3], pid_fields[5], pid_fields[7], pid_fields[8], pid_fields[11], pid_fields[13], pid_fields[15], pid_fields[16], pid_fields[19], pid_fields[18], pid_fields[29])

@dataclass
class PV1_Data:
    set_id_pv1: str
    patient_class: str
    assigned_patient_location: str
    admission_type: str
    preadmit_number: str
    prior_patient_location: str
    attending_doctor: str
    referring_doctor: str
    consulting_doctor: str
    hospital_service: str
    patient_type: str
    visit_number: str
    discharge_disposition: str
    admit_date_time: str
    discharge_date_time: str

class Hl7PV1Decoder:
    def __init__(self, PV1_Segment, encoding_characters):
        self.PV1_Segment = PV1_Segment
        self.field_separator = PV1_Segment[3]
        self.encoding_characters = encoding_characters

    def decode_segment(self) -> PV1_Data:
        pv1_fields = get_segment_fields(self.PV1_Segment, self.field_separator)
        if any(field != '' for i, field in enumerate(pv1_fields) if i not in [1,2,3,4,5,6,7,8,9,10,18,19,36,44,45]):
            print(f"Warnung: das Patient Visit Segment enthält weitere Felder die noch nicht vom Decoder abgedeckt wurden")
        return PV1_Data(pv1_fields[1], pv1_fields[2], pv1_fields[3], pv1_fields[4], pv1_fields[5], pv1_fields[6], pv1_fields[7], pv1_fields[8], pv1_fields[9], pv1_fields[10], pv1_fields[18], pv1_fields[19], pv1_fields[36], pv1_fields[44], pv1_fields[45])

@dataclass
class TXA_Data:
    set_id: str
    document_type: str
    document_content_presentation: str
    datetime_activity: str
    primary_activity_provider: str
    datetime_origination: str
    datetime_transcription: str
    datetime_last_edit: str
    originator: str
    assigned_document_authenticator: str
    transcriptionist: str
    unique_document_number: str
    parent_document_number: str
    placer_order_number: str
    filler_order_number: str
    unique_document_file_name: str
    document_completion_status: str
    document_confidentiality_status: str
    document_availability_status: str
    document_storage_status: str
    document_change_reason: str
    authentication_person_timestamp: str

class Hl7TXADecoder:
    def __init__(self, TXA_Segment, encoding_characters):
        self.TXA_Segment = TXA_Segment
        self.field_separator = TXA_Segment[3]
        self.encoding_characters = encoding_characters

    def decode_segment(self) -> TXA_Data:
        txa_fields = get_segment_fields(self.TXA_Segment, self.field_separator)
        if any(field != '' for i, field in enumerate(txa_fields) if i not in [x for x in range(1,22)]):
            print(f"Warnung: das Transcription Document Header Segment enthält weitere Felder die noch nicht vom Decoder abgedeckt wurden")
        return PV1_Data(txa_fields[1], txa_fields[2], txa_fields[3], txa_fields[4], txa_fields[5], txa_fields[6], txa_fields[7], txa_fields[8], txa_fields[9], txa_fields[10], txa_fields[11], 
                        txa_fields[12], txa_fields[13], txa_fields[14], txa_fields[15], txa_fields[16], txa_fields[17], txa_fields[18], txa_fields[19], txa_fields[20], txa_fields[21], txa_fields[22])
        
@dataclass
class OBX_Data:
    set_id: int                     # OBX-1
    value_type: str                 # OBX-2
    observation_identifier: str     # OBX-3
    observation_sub_id: str         # OBX-4
    observation_value: str          # OBX-5
    units: str                      # OBX-6
    reference_range: str            # OBX-7
    abnormal_flags: str             # OBX-8
    observation_result_status: str  # OBX-11
    observation_datetime: str       # OBX-14
    responsible_observer: str       # OBX-16
    observation_method: str         # OBX-17

class OBX_Data_List:
    def __init__(self):
        self.number_elements: int = 0
        self.__obx_segment_list: list[OBX_Data] = [] 

    def add_obx_segment(self, obx_segment: OBX_Data) -> bool:
        if next((i for i, obx_segment_cmp in enumerate(self.__obx_segment_list) if obx_segment.set_id == obx_segment_cmp.set_id), None) is not None:
            print("Die set_id des hinzuzufügenden OBX Segments ist bereits in der Liste vorhanden und kann nicht hinzugefügt werden")
            return False
        self.__obx_segment_list.append(obx_segment)
        self.number_elements += 1
        return True

    def delete_obx_segment_by_set_id(self, set_id) -> OBX_Data|bool:
        list_index = next((i for i, obx_segment in enumerate(self.__obx_segment_list) if obx_segment.set_id == set_id), None)
        if list_index is not None:
            deleted_obx_segment = self.__obx_segment_list.pop(list_index)
            return deleted_obx_segment
        else:
            print(f"Es ist kein OBX Segment mit der set_id {set_id} in der Liste vorhanden")
            return False
        
    def get_obx_segment_list(self) -> list[OBX_Data]:
        return self.__obx_segment_list.copy()

class Hl7OBXDecoder: #TODO
    """
    @brief Erstellt ein OBX_Data Objekt aus einem OBX_Segment einer HL7-Nachricht
    """
    def __init__(self, OBX_Segment, encoding_characters):
        self.OBX_Segment = OBX_Segment
        self.field_separator = OBX_Segment[3]
        self.encoding_characters = encoding_characters
    
    def decode_segment(self) -> OBX_Data:
        obx_fields = get_segment_fields(self.OBX_Segment, self.field_separator)
        if any(field != '' for i, field in enumerate(obx_fields) if i not in [1,2,3,4,5,6,7,8,11,14,16,17]):
            print(f"Warnung: das Observation Result Segment enthält weitere Felder die noch nicht vom Decoder abgedeckt wurden")
        return OBX_Data(int(obx_fields[1]), obx_fields[2], obx_fields[3], obx_fields[4], obx_fields[5], obx_fields[6], obx_fields[7], obx_fields[8], obx_fields[11], obx_fields[14], obx_fields[16], obx_fields[17])

def get_segment_fields(segment: str, sep: str='|') -> list[str]:
    """
    @brief erstellt eine Liste aus dem String Segment mit den einzelnen Werten

    @param segment [str] das Segment der HL7-Nachricht
    @sep [str] der Separator der im Segment genutzt wird um die einzelnen Werte zu trennen

    @return [list[str]] Die Liste mit den einzelnen Werten
    """
    return [field for field in segment.split(sep)]

def str_to_datetime(s: str) -> datetime:
    """
    @brief erstellt aus einem String ein datetime Objekt

    Die Methode ertsellt ein datetime Objekt aus einem string welches im in HL7-Nachrichten üblichen Format "%Y%m%d%H%M%S" vorliegt

    @param s [str] Der String der in ein datetime Objekt konvertiert werden soll

    @return [datetime] das datetime Objekt  
    """
    return datetime.strptime(
        s, "%Y%m%d%H%M%S"
    )

@dataclass
class HL7Data():
    msh_segment: MSH_Data
    sft_segment: SFT_Data
    evn_segment: EVN_Data
    pid_segment: PID_Data
    pv1_segment: PV1_Data
    txa_segment: TXA_Data
    obx_segment_list: OBX_Data_List