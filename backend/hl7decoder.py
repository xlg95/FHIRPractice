class Hl7Decoder:
    def __init__(self, message, validate=True):
        self.message = message
        if validate and self.__validateMessage():
            print("Message validated")
        self.MSH = None

    def __validateMessage(self) -> bool:
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
            neededFields = {"MSH": {"needed": [1],   "name": "Message Header"},
                            "SFT": {"needed": [0,1], "name": "Software Information"},
                            "EVN": {"needed": [1],   "name": "Event Information"},
                            "PID": {"needed": [1],   "name": "Patient Information"},
                            "PV1": {"needed": [0,1], "name": "Patient Visit"},
                            "TXA": {"needed": [1],   "name": "Transcription Document Header"},
                            "OBX": {"name": "Observation Result"}} # TODO: In config File auslagern!!!
            for neededField, fieldData in neededFields.items():
                if "needed" in fieldData:
                    if (numberFieldSegments:= sum(1 for segment in self.message.split("\n") if segment.startswith(neededField))) not in fieldData["needed"]:
                        raise Exception(f"Es wurden {numberFieldSegments} {fieldData["name"]} Segmente gefunden! Die erforderliche Anzahl ist: {fieldData}! Bitte überprüfen Sie die HL7-Nachricht")
            
            wrongSegments = [segment[:3] for segment in self.message.split("\n") if segment[:3] not in neededFields]
            if wrongSegments:
                raise Exception(f"Es wurde mindestens ein Feld gefunden, welches nicht in eine MDM_T02 HL7 Nachricht gehört! Falsche Felder: {wrongSegments}")
            return True
                
    def decodeMessage(self):
        pass

    def decodeMSH(self):
        MSHSegment = next(s for s in self.message.split("\n") if s.startswith("MSH"))
        print(f"MSHSegment: {MSHSegment}")






class Hl7MSHDecoder:
    def __init__(self, MSH_Segment):
        pass