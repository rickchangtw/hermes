"""
會議記錄資料庫模型
PostgreSQL 表結構定義與操作

從 shared-wiki/scripts/meeting-data-model.py 遷移，
適配 Hermes Agent Fork apps/meeting/ 生態系統。
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

# 資料庫配置
DB_CONFIG = {
    "host": os.environ.get("COMMUNITY_DB_HOST", "localhost"),
    "port": int(os.environ.get("COMMUNITY_DB_PORT", 5432)),
    "dbname": os.environ.get("COMMUNITY_DB_NAME", "community"),
    "user": os.environ.get("COMMUNITY_DB_USER", "hermes"),
    "password": os.environ.get("COMMUNITY_DB_PASSWORD", "hermes123"),
}

# 6 張核心表結構
TABLES: Dict[str, dict] = {
    "meetings": {
        "name": "meetings",
        "columns": {
            "meeting_id": "VARCHAR(50) PRIMARY KEY",
            "title": "VARCHAR(200) NOT NULL",
            "date": "DATE NOT NULL",
            "time_start": "TIME NOT NULL",
            "time_end": "TIME NOT NULL",
            "location": "VARCHAR(200) DEFAULT '社區活動中心'",
            "host": "VARCHAR(100) NOT NULL",
            "agenda": "JSONB",
            "action_items": "JSONB",
            "created_at": "TIMESTAMP DEFAULT NOW()",
            "updated_at": "TIMESTAMP DEFAULT NOW()",
        },
        "description": "社區會議記錄",
    },
    "meeting_speakers": {
        "name": "meeting_speakers",
        "columns": {
            "id": "SERIAL PRIMARY KEY",
            "meeting_id": "VARCHAR(50) REFERENCES meetings(meeting_id)",
            "speaker_name": "VARCHAR(100) NOT NULL",
            "speaker_unit": "VARCHAR(10)",
            "speaker_role": "VARCHAR(50)",
            "voice_profile_id": "UUID",
            "created_at": "TIMESTAMP DEFAULT NOW()",
        },
        "description": "會議發言人",
    },
    "meeting_segments": {
        "name": "meeting_segments",
        "columns": {
            "id": "SERIAL PRIMARY KEY",
            "meeting_id": "VARCHAR(50) REFERENCES meetings(meeting_id)",
            "speaker_id": "INTEGER REFERENCES meeting_speakers(id)",
            "start": "REAL NOT NULL",
            "end": "REAL NOT NULL",
            "text": "TEXT NOT NULL",
            "confidence": "REAL DEFAULT 0.0",
        },
        "description": "會議語音段",
    },
    "meeting_action_items": {
        "name": "meeting_action_items",
        "columns": {
            "id": "SERIAL PRIMARY KEY",
            "meeting_id": "VARCHAR(50) REFERENCES meetings(meeting_id)",
            "item": "TEXT NOT NULL",
            "owner": "VARCHAR(100)",
            "deadline": "DATE",
            "status": "VARCHAR(20) DEFAULT 'pending'",
            "created_at": "TIMESTAMP DEFAULT NOW()",
        },
        "description": "會議行動項目",
    },
    "meeting_files": {
        "name": "meeting_files",
        "columns": {
            "id": "SERIAL PRIMARY KEY",
            "meeting_id": "VARCHAR(50) REFERENCES meetings(meeting_id)",
            "file_name": "VARCHAR(255) NOT NULL",
            "file_path": "TEXT NOT NULL",
            "file_type": "VARCHAR(50) DEFAULT 'audio'",
            "file_size": "BIGINT",
            "created_at": "TIMESTAMP DEFAULT NOW()",
        },
        "description": "會議相關文件",
    },
    "meeting_notes": {
        "name": "meeting_notes",
        "columns": {
            "id": "SERIAL PRIMARY KEY",
            "meeting_id": "VARCHAR(50) REFERENCES meetings(meeting_id)",
            "note": "TEXT NOT NULL",
            "note_type": "VARCHAR(50) DEFAULT 'general'",
            "created_by": "VARCHAR(100)",
            "created_at": "TIMESTAMP DEFAULT NOW()",
        },
        "description": "會議筆記",
    },
}


def generate_create_tables_sql() -> List[str]:
    """生成建表 SQL 語句"""
    sql_statements = []

    for table_name, table_info in TABLES.items():
        columns = ", ".join(
            f"{col_name} {col_type}"
            for col_name, col_type in table_info["columns"].items()
        )
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        sql_statements.append(sql)

        for col_name, col_type in table_info["columns"].items():
            if "VARCHAR" in col_type.upper() and "REFERENCES" not in col_type.upper():
                sql_statements.append(
                    f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{col_name} "
                    f"ON {table_name} ({col_name})"
                )

    return sql_statements


def get_connection():
    """獲取 PostgreSQL 連線"""
    import psycopg2
    return psycopg2.connect(**DB_CONFIG)


def create_tables(conn=None) -> bool:
    """建立所有會議相關表"""
    should_close = conn is None
    try:
        if conn is None:
            conn = get_connection()

        cursor = conn.cursor()
        for sql in generate_create_tables_sql():
            cursor.execute(sql)
        conn.commit()
        cursor.close()

        if should_close:
            conn.close()
        return True
    except Exception as e:
        print(f"⚠️ 建立會議表失敗: {e}")
        return False


def save_meeting_record(
    meeting_id: str,
    title: str = "社區會議",
    date: str = None,
    time_start: str = "09:00",
    time_end: str = "10:00",
    location: str = "社區活動中心",
    host: str = "總幹事",
    agenda: list = None,
    action_items: list = None,
) -> bool:
    """保存會議記錄到資料庫"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO meetings (meeting_id, title, date, time_start, time_end,
                                      location, host, agenda, action_items,
                                      created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
               ON CONFLICT (meeting_id) DO UPDATE SET updated_at = NOW()""",
            (
                meeting_id,
                title,
                date or datetime.now().date().isoformat(),
                time_start,
                time_end,
                location,
                host,
                json.dumps(agenda or [], ensure_ascii=False),
                json.dumps(action_items or [], ensure_ascii=False),
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ 保存會議記錄失敗: {e}")
        return False


def generate_sample_data() -> dict:
    """生成示例數據"""
    return {
        "meetings": [
            {
                "meeting_id": "MEET-2026-07-15",
                "title": "社區會議",
                "date": "2026-07-15",
                "time_start": "09:00",
                "time_end": "10:00",
                "location": "社區活動中心",
                "host": "張三",
                "agenda": [
                    {
                        "title": "停車場收費",
                        "speaker": "李四",
                        "content": "討論新的收費標準",
                        "resolution": "通過",
                    },
                    {
                        "title": "消防設備更新",
                        "speaker": "王五",
                        "content": "討論設備更新預算",
                        "resolution": "待簽核",
                    },
                ],
                "action_items": [
                    {
                        "item": "完成停車場收費方案",
                        "owner": "李四",
                        "deadline": "2026-07-22",
                        "status": "pending",
                    },
                    {
                        "item": "消防設備更新申請",
                        "owner": "王五",
                        "deadline": "2026-07-29",
                        "status": "pending",
                    },
                ],
            }
        ],
        "meeting_speakers": [
            {"speaker_name": "張三", "speaker_unit": "101", "speaker_role": "總幹事"},
            {"speaker_name": "李四", "speaker_unit": "205", "speaker_role": "委員"},
            {"speaker_name": "王五", "speaker_unit": "308", "speaker_role": "委員"},
        ],
        "meeting_segments": [
            {
                "speaker_id": 1,
                "start": 0.0,
                "end": 10.0,
                "text": "歡迎大家參加今天的社區會議",
                "confidence": 0.95,
            },
            {
                "speaker_id": 2,
                "start": 10.0,
                "end": 20.0,
                "text": "首先討論停車場收費問題",
                "confidence": 0.92,
            },
        ],
    }