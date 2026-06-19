EVENT_TIMING: dict[str, list[str, str, str]] = {
    "MORN": ["Morning", "Event occurs during the morning. The exact time is unspecified and established by institution convention or patient interpretation.", "m"],
    "MORN.early": ["Early Morning", "Event occurs during the early morning. The exact time is unspecified and established by institution convention or patient interpretation.", ""],
    "MORN.late": ["Late Morning", "Event occurs during the late morning. The exact time is unspecified and established by institution convention or patient interpretation.", ""],
    "NOON": ["Noon", "Event occurs around 12:00pm. The exact time is unspecified and established by institution convention or patient interpretation.", "d"],
    "AFT": ["Afternoon", "Event occurs during the afternoon. The exact time is unspecified and established by institution convention or patient interpretation.", ""],
    "AFT.early": ["Early Afternoon", "Event occurs during the early afternoon. The exact time is unspecified and established by institution convention or patient interpretation.", ""],
    "AFT.late": ["Late Afternoon", "Event occurs during the late afternoon. The exact time is unspecified and established by institution convention or patient interpretation.", ""],
    "EVE": ["Evening", "Event occurs during the evening. The exact time is unspecified and established by institution convention or patient interpretation.", "v"],
    "EVE.early": ["Early Evening", "Event occurs during the early evening. The exact time is unspecified and established by institution convention or patient interpretation.", ""],
    "EVE.late": ["Late Evening", "Event occurs during the late evening. The exact time is unspecified and established by institution convention or patient interpretation.", ""],
    "NIGHT": ["Night", "Event occurs during the night. The exact time is unspecified and established by institution convention or patient interpretation.", ""],
    "PHS": ["After Sleep", "Event occurs [offset] after subject goes to sleep. The exact time is unspecified and established by institution convention or patient interpretation.", ""],
}

BMP_KEY_TO_EVENT: dict[str, str]{
    "m": "MORN",
    "d": "NOON",
    "v": "EVE"
}