class Hl7Decoder:
    def __init__(self, message, validate=True):
        self.message = message
        if validate and self.__validateMessage():
            print("Message validated")
        self.MSH_decoded = None

    def __validateMessage(self) -> bool: # Kann nur HL7-Nachrichten vom Typ MDM_T02 validieren
        try:
            MSHSegment = next(segment for segment in self.message.split("\n") if segment.startswith("MSH"))
            MessageType = MSHSegment.split("|")[8]
            MessageCode = MessageType.split("^")[0]
            TriggerEvent = MessageType.split("^")[1]
            print(MessageType)
        except:
            raise Exception("Es wurde kein Messageheader gefunden! Bitte überprüfen Sie die HL7-Nachricht")
        if f"{MessageCode}_{TriggerEvent}" != "MDM_T02":
            print(f"!!!WARNUNG: Derzeit können nur HL7-Nachrichten vom Typ MDM_T02 validiert und korrekte Dekodierung garantiert werden. Ihre Nachricht ist vom Typ {MessageCode}_{TriggerEvent}. Bitte wenden Sie sich an den Entwickler Ihres Vertrauens! (lxg)")
            return False
        else:
            neededFields = {"MSH": {"numberNeeded": [1],   "name": "Message Header"},
                            "SFT": {"numberNeeded": [0,1], "name": "Software Information"},
                            "EVN": {"numberNeeded": [1],   "name": "Event Information"},
                            "PID": {"numberNeeded": [1],   "name": "Patient Information"},
                            "PV1": {"numberNeeded": [0,1], "name": "Patient Visit"},
                            "TXA": {"numberNeeded": [1],   "name": "Transcription Document Header"},
                            "OBX": {"name": "Observation Result"}} # TODO: In config File auslagern!!!
            for neededField, fieldData in neededFields.items():
                if "numberNeeded" in fieldData:
                    if (numberFieldSegments:= sum(1 for segment in self.message.split("\n") if segment.startswith(neededField))) not in fieldData["numberNeeded"]:
                        raise Exception(f"Es wurden {numberFieldSegments} {fieldData["name"]} Segmente gefunden! Die erforderliche Anzahl ist: {fieldData}! Bitte überprüfen Sie die HL7-Nachricht")
                    
            wrongSegments = [segment[:3] for segment in self.message.split("\n") if segment[:3] not in neededFields]
            if wrongSegments:
                raise Exception(f"Es wurde mindestens ein Feld gefunden, welches nicht in eine MDM_T02 HL7 Nachricht gehört! Falsche Felder: {wrongSegments}")
            return True
                
    def decodeMessage(self):
        pass

    def decodeMSH(self):
        MSH_Segment = next(s for s in self.message.split("\n") if s.startswith("MSH"))
        msh_decoder = Hl7MSHDecoder(MSH_Segment)
        self.MSH_decoded = msh_decoder.decodeMSH_Segement()



class Hl7MSHDecoder:
    def __init__(self, MSH_Segment):
        self.MSH_Segment = MSH_Segment
        self.field_separator = MSH_Segment[3]
        self.encoding_characters = None

    def decodeMSH_Segement(self) -> MSH_Segment:
        MSH_fields = [field for field in self.MSH_Segment.split(self.field_separator)]
        self.encoding_characters = MSH_fields[1] #TODO: Find out how to encode strings with encoding_characters better
        if any(field != '' for field in MSH_fields[12:]):
            print(f"Warnung: das Message Header Segment enthält weitere Felder die noch nicht vom Decoder abgedeckt wurden")
        return MSH_Segment(self.field_separator, self.encoding_characters, MSH_fields[2], MSH_fields[3], MSH_fields[4], 
                           MSH_fields[5], MSH_fields[6], MSH_fields[7], MSH_fields[8], MSH_fields[9], MSH_fields[10], MSH_fields[11])
        
class MSH_Segment:
    def __init__(self, 
                 field_separator, 
                 encoding_characters, 
                 sending_application,
                 sending_facility,
                 receiving_application,
                 receiving_facility,
                 datetime_of_message,
                 security,
                 message_type,
                 message_control_id,
                 processing_id,
                 version_id):
        self.field_separator = field_separator
        self.encoding_characters = encoding_characters
        self.sending_application = sending_application
        self.sending_facility = sending_facility
        self.receiving_application = receiving_application
        self.receiving_facility = receiving_facility
        self.datetime_of_message = datetime_of_message
        self.security = security
        self.message_type = message_type
        self.message_control_id = message_control_id
        self.processing_id = processing_id
        self.version_id = version_id