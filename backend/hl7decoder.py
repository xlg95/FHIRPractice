from dataclasses import dataclass
from datetime import datetime
from hl7_data import HL7Data, Hl7MSHDecoder, Hl7SFTDecoder, Hl7EVNDecoder, Hl7PIDDecoder, Hl7PV1Decoder, Hl7TXADecoder, Hl7OBXDecoder
from hl7_data import MSH_Data, SFT_Data, EVN_Data, PID_Data, PV1_Data, TXA_Data, OBX_Data_List

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
        self.OBX_decoded_data_list: OBX_Data_List = OBX_Data_List()

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

    def decodeMessage(self) -> HL7Data:
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
            self.OBX_decoded_data_list.append_obx_segment(obx_segment= obx_decoder.decode_segment())




