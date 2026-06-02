class Hl7Decoder:
    def __init__(self, message):
        self.message = message
        self.__validateMessage()
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
            return True
        if sum(1 for segment in self.message.split("\n") if segment.startswith("MSH")) != 1:
            raise Exception("Es wurden zu viele Messageheader gefunden! Bitte überprüfen Sie die HL7-Nachricht")
        if (numberSoftwareInformation:= sum(1 for segment in self.message.split("\n") if segment.startswith("SFT"))) > 1:
            raise Exception(f"Es wurden {numberSoftwareInformation} Software Information Segmente gefunden! Die erforderliche Anzahl ist: 0 bis 1! Bitte überprüfen Sie die HL7-Nachricht")
        if (numberEventInformation:= sum(1 for segment in self.message.split("\n") if segment.startswith("EVN"))) != 1:
            raise Exception(f"Es wurden {numberEventInformation} Event Information Segmente gefunden! Die erforderliche Anzahl ist: 1! Bitte überprüfen Sie die HL7-Nachricht")
        if (numberPatientInformation:= sum(1 for segment in self.message.split("\n") if segment.startswith("PID"))) != 1:
            raise Exception(f"Es wurden {numberPatientInformation} Patient Information Segmente gefunden! Die erforderliche Anzahl ist: 1! Bitte überprüfen Sie die HL7-Nachricht")
        if (numberPatientVisit:= sum(1 for segment in self.message.split("\n") if segment.startswith("PV1"))) > 1:
            raise Exception(f"Es wurden {numberPatientVisit} Patient Visit Segmente gefunden! Die erforderliche Anzahl ist: 0 bis 1! Bitte überprüfen Sie die HL7-Nachricht")
        if (numberTranscriptionDocumentHeader:= sum(1 for segment in self.message.split("\n") if segment.startswith("TXA"))) != 1:
            raise Exception(f"Es wurden {numberTranscriptionDocumentHeader} Transcription Document Header Segmente gefunden! Die erforderliche Anzahl ist: 1! Bitte überprüfen Sie die HL7-Nachricht")

    def decodeMessage(self):
        pass

    def decodeMSH(self):
        MSHSegment = next(s for s in self.message.split("\n") if s.startswith("MSH"))
        print(f"MSHSegment: {MSHSegment}")






class Hl7MSHDecoder:
    def __init__(self, MSH_Segment):
        pass