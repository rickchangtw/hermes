"""
Conference Recorder - 會議記錄引擎

基於 Silero VAD + Whisper + 發言人辨識的會議記錄系統。
提供語音轉文字、發言人識別、會議記錄生成、PostgreSQL 儲存等功能。
"""

from .recorder import (
    MeetingTranscriptionSystem,
    MeetingRecord,
    TranscriptionSegment,
    Speaker,
    MODEL_PATHS,
    VOICE_DB_PATH,
)
from .models import (
    DB_CONFIG,
    TABLES,
    create_tables,
    save_meeting_record,
    get_connection,
    generate_create_tables_sql,
    generate_sample_data,
)
from .realtime import (
    RealtimeTranscriber,
    create_server,
    create_fastapi_app,
    save_meeting_to_db,
    load_models,
    SYSTEM_STATUS,
)

__all__ = [
    # recorder
    "MeetingTranscriptionSystem",
    "MeetingRecord",
    "TranscriptionSegment",
    "Speaker",
    "MODEL_PATHS",
    "VOICE_DB_PATH",
    # models
    "DB_CONFIG",
    "TABLES",
    "create_tables",
    "save_meeting_record",
    "get_connection",
    "generate_create_tables_sql",
    "generate_sample_data",
    # realtime
    "RealtimeTranscriber",
    "create_server",
    "create_fastapi_app",
    "save_meeting_to_db",
    "load_models",
    "SYSTEM_STATUS",
]