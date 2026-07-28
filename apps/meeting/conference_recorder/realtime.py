"""
實時會議轉錄系統

基於 Silero VAD + Whisper + 發言人辨識 + WebSocket/FastAPI 即時推送。
從 shared-wiki/scripts/realtime-meeting-transcription.py 遷移，
適配為 Hermes Agent Fork apps/meeting/conference_recorder/ 模組。

注意：此模組參考了 meeting-transcription skill 中的已知問題和修復方案：
- 不使用 @app.on_event("startup"/"shutdown") (會與 uvicorn.run() 衝突)
- Silero VAD 使用 v6.2.1+ API (load_silero_vad + model(chunk, sr=16000))
- 不存在 language_probability，使用 avg_log_prob
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

# 日誌配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 資料庫配置
DB_CONFIG = {
    "host": os.environ.get("COMMUNITY_DB_HOST", "localhost"),
    "port": int(os.environ.get("COMMUNITY_DB_PORT", 5432)),
    "dbname": os.environ.get("COMMUNITY_DB_NAME", "community"),
    "user": os.environ.get("COMMUNITY_DB_USER", "hermes"),
    "password": os.environ.get("COMMUNITY_DB_PASSWORD", "hermes123"),
}

# 模型路徑
MODELS_DIR = Path(os.environ.get("MODELS_DIR", "/home/rick/models"))

# 系統狀態
SYSTEM_STATUS: dict = {
    "running": False,
    "meeting_id": None,
    "speakers": {},
    "current_speaker": None,
    "is_speaking": False,
    "transcription_buffer": "",
    "confidence": 0.0,
    "start_time": None,
    "end_time": None,
}

# 發言人特徵庫（簡化關鍵字匹配）
SPEAKER_PROFILES = {
    "張三": {"keywords": ["討論", "意見", "建議"], "unit": "101", "confidence": 0.85},
    "李四": {"keywords": ["停車場", "收費", "預算"], "unit": "205", "confidence": 0.90},
    "王五": {"keywords": ["消防", "設備", "更新"], "unit": "308", "confidence": 0.88},
}

# 模型全域變數 (lazy loading)
_vad_model = None
_whisper_model = None

# WebSocket 連線管理
connected_clients: list = []


def load_models():
    """載入 Silero VAD + Whisper 模型"""
    global _vad_model, _whisper_model

    logger.info("載入 Silero VAD 模型...")
    try:
        from silero_vad import load_silero_vad
        _vad_model = load_silero_vad()
        logger.info("Silero VAD 模型載入完成")
    except ImportError:
        logger.warning("⚠️ silero_vad 未安裝，VAD 功能不可用")
        _vad_model = None

    logger.info("載入 Whisper 模型 (base)...")
    try:
        import whisper
        import torch
        _whisper_model = whisper.load_model(
            name="base",
            device="cuda" if torch.cuda.is_available() else "cpu",
        )
        logger.info("Whisper 模型載入完成")
    except ImportError:
        logger.warning("⚠️ whisper 未安裝，轉錄功能不可用")
        _whisper_model = None


class RealtimeTranscriber:
    """實時轉錄器 - 處理音頻塊並推送轉錄結果"""

    def __init__(self):
        global _vad_model, _whisper_model
        if _vad_model is None or _whisper_model is None:
            load_models()

    def process_audio_chunk(self, audio_data: bytes) -> Optional[dict]:
        """處理音頻塊，返回轉錄結果"""
        global _vad_model, _whisper_model

        if _vad_model is None or _whisper_model is None:
            return None

        audio_np = np.frombuffer(audio_data, dtype=np.float32)

        # Silero VAD v6.2.1+ API
        import torch
        if len(audio_np) > 512:
            audio_tensor = torch.from_numpy(audio_np[:512])
        else:
            padded = np.pad(audio_np, (0, 512 - len(audio_np)))
            audio_tensor = torch.from_numpy(padded)

        result = _vad_model(audio_tensor, sr=16000)
        speech_prob = result.item()

        if speech_prob < 0.5:
            return None  # 非語音段，跳過

        # Whisper 轉錄
        transcription = self._transcribe(audio_np)
        if not transcription:
            return None

        # 發言人識別
        speaker = self._identify_speaker(transcription)

        return {
            "type": "transcription",
            "meeting_id": SYSTEM_STATUS.get("meeting_id"),
            "speaker": speaker["name"] if speaker else "unknown",
            "unit": speaker.get("unit", "") if speaker else "",
            "text": transcription,
            "confidence": speaker["confidence"] if speaker else 0.0,
            "timestamp": datetime.now().isoformat(),
        }

    def _transcribe(self, audio_np: np.ndarray) -> str:
        """Whisper 語音轉文字"""
        global _whisper_model
        if _whisper_model is None:
            return ""

        if len(audio_np) > 16000:
            audio_16k = audio_np[:16000]
        else:
            audio_16k = np.pad(audio_np, (0, 16000 - len(audio_np)))

        result = _whisper_model.transcribe(
            audio_16k, language="zh", task="transcribe", fp16=False
        )
        return result.get("text", "").strip()

    def _identify_speaker(self, transcription: str) -> dict:
        """發言人識別（基於關鍵字）"""
        for name, profile in SPEAKER_PROFILES.items():
            if any(kw in transcription for kw in profile["keywords"]):
                return {
                    "name": name,
                    "unit": profile["unit"],
                    "confidence": profile["confidence"],
                }
        return {"name": "未知發言人", "unit": "", "confidence": 0.0}


def save_meeting_to_db(meeting_id: str) -> bool:
    """保存會議記錄到 PostgreSQL"""
    try:
        import psycopg2

        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO meetings (meeting_id, title, date, time_start,
                                      time_end, location, host, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
               ON CONFLICT (meeting_id) DO UPDATE SET updated_at = NOW()""",
            (
                meeting_id,
                "社區會議",
                datetime.now().date(),
                "09:00",
                "10:00",
                "社區活動中心",
                "張三",
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"會議記錄已保存：{meeting_id}")
        return True
    except Exception as e:
        logger.error(f"保存會議記錄錯誤：{e}")
        return False


def create_fastapi_app():
    """創建 FastAPI 應用程式 (給 external 使用)"""

    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(title="實時會議轉錄系統", version="2.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 初始化系統狀態
    SYSTEM_STATUS["running"] = True
    SYSTEM_STATUS["meeting_id"] = f"MEET-{datetime.now().strftime('%Y-%m-%d')}"

    transcriber = RealtimeTranscriber()

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "system": "realtime-meeting-transcription",
            "running": SYSTEM_STATUS["running"],
            "speakers_count": len(SYSTEM_STATUS["speakers"]),
            "device": "cpu",
        }

    @app.get("/api/status")
    async def get_status():
        return {
            "running": SYSTEM_STATUS["running"],
            "meeting_id": SYSTEM_STATUS["meeting_id"],
            "speakers": list(SYSTEM_STATUS["speakers"].keys()),
            "current_speaker": SYSTEM_STATUS["current_speaker"],
            "is_speaking": SYSTEM_STATUS["is_speaking"],
            "confidence": SYSTEM_STATUS["confidence"],
        }

    @app.post("/api/start-meeting")
    async def start_meeting(meeting_data: dict):
        meeting_id = meeting_data.get(
            "meeting_id", f"MEET-{datetime.now().strftime('%Y-%m-%d')}"
        )
        SYSTEM_STATUS["meeting_id"] = meeting_id
        SYSTEM_STATUS["speakers"] = {}
        SYSTEM_STATUS["current_speaker"] = None
        SYSTEM_STATUS["transcription_buffer"] = ""
        SYSTEM_STATUS["start_time"] = datetime.now().isoformat()
        SYSTEM_STATUS["end_time"] = None
        logger.info(f"會議開始：{meeting_id}")
        return {"status": "ok", "meeting_id": meeting_id}

    @app.post("/api/end-meeting")
    async def end_meeting():
        SYSTEM_STATUS["end_time"] = datetime.now().isoformat()
        SYSTEM_STATUS["running"] = False
        meeting_id = SYSTEM_STATUS["meeting_id"]

        # 保存到資料庫
        save_meeting_to_db(meeting_id)

        logger.info(f"會議結束：{meeting_id}")
        return {"status": "ok", "meeting_id": meeting_id}

    @app.websocket("/ws/transcription")
    async def ws_transcription(websocket: WebSocket):
        await websocket.accept()
        logger.info("WebSocket 連接已建立")

        try:
            while SYSTEM_STATUS["running"]:
                data = await websocket.receive_json()

                if data.get("type") == "audio_chunk":
                    raw = data.get("audio_data", b"")
                    if isinstance(raw, str):
                        raw = raw.encode()
                    result = transcriber.process_audio_chunk(raw)
                    if result:
                        await websocket.send_json(result)
                        SYSTEM_STATUS["transcription_buffer"] += result["text"]

                elif data.get("type") == "control":
                    cmd = data.get("command", "")
                    if cmd == "clear_buffer":
                        SYSTEM_STATUS["transcription_buffer"] = ""
                    logger.info(f"控制指令: {cmd}")

        except WebSocketDisconnect:
            logger.info("WebSocket 連接斷開")
        except Exception as e:
            logger.error(f"WebSocket 錯誤: {e}")

    return app


def create_server(host: str = "0.0.0.0", port: int = 3020):
    """創建 HTTP 伺服器 (基於 stdlib，用於後台服務)"""
    import http.server
    from socketserver import ThreadingMixIn

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "status": "ok",
                            "system": "meeting-recorder",
                            "running": SYSTEM_STATUS["running"],
                            "meeting_id": SYSTEM_STATUS["meeting_id"],
                        }
                    ).encode()
                )
            elif self.path == "/api/status":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "running": SYSTEM_STATUS["running"],
                            "meeting_id": SYSTEM_STATUS["meeting_id"],
                            "speakers": list(SYSTEM_STATUS["speakers"].keys()),
                        }
                    ).encode()
                )
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            pass

    class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    return ThreadedHTTPServer((host, port), Handler)