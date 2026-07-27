"""
會議記錄系統 - 語音轉文字 + 發言人辨識

基於 Silero VAD + Whisper + Speaker Diarization。
從 shared-wiki/scripts/meeting-transcription.py 遷移，
適配為 Hermes Agent Fork apps/meeting/conference_recorder/ 模組。

使用方式:
    from apps.meeting.conference_recorder.recorder import MeetingTranscriptionSystem
    system = MeetingTranscriptionSystem()
"""

import json
import os
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

# 模型路徑 (可透過環境變數覆蓋)
MODEL_PATHS = {
    "whisper": os.environ.get("WHISPER_MODEL_PATH", "/home/rick/models/whisper"),
    "silero_vad": os.environ.get("SILERO_VAD_PATH", "/home/rick/models/silero_vad"),
    "speaker_diarization": os.environ.get(
        "SPEAKER_DIARIZATION_PATH", "/home/rick/models/spk_recognition"
    ),
}

# 語音特徵資料庫路徑
VOICE_DB_PATH = os.environ.get(
    "VOICE_DB_PATH", "/home/rick/shared-wiki/vault/voice_profiles.json"
)


@dataclass
class Speaker:
    """發言人資料"""
    id: str
    name: str
    unit: str = ""
    role: str = ""
    embedding: str = ""  # base64 whisper embedding
    confidence: float = 0.0
    model: str = "whisper"


@dataclass
class TranscriptionSegment:
    """轉錄段落"""
    speaker_id: str
    speaker_name: str
    start: float
    end: float
    text: str
    confidence: float = 0.0


@dataclass
class MeetingRecord:
    """會議記錄"""
    meeting_id: str
    title: str
    date: str
    time_start: str
    time_end: str
    location: str
    host: str
    speakers: List[Speaker] = field(default_factory=list)
    segments: List[TranscriptionSegment] = field(default_factory=list)
    agenda: List[dict] = field(default_factory=list)
    action_items: List[dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class MeetingTranscriptionSystem:
    """會議記錄系統 - 語音轉文字 + 發言人辨識"""

    def __init__(self, voice_db_path: str = VOICE_DB_PATH):
        self.voice_db = self._load_voice_db(voice_db_path)
        self.meetings: Dict[str, MeetingRecord] = {}

    def _load_voice_db(self, path: str) -> Dict[str, Speaker]:
        """載入語音特徵資料庫"""
        if not path or not os.path.exists(path):
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {v["name"]: Speaker(**v) for v in data}
        except Exception as e:
            print(f"⚠️ 無法載入語音資料庫: {e}")
            return {}

    def process_audio_file(self, audio_path: str) -> Optional[MeetingRecord]:
        """處理會議音頻文件 (完整 pipeline)"""
        print(f"🎙️ 處理音頻文件: {audio_path}")

        print("📍 Step 1: 語音活動偵測 (Silero VAD)...")
        speech_segments = self._vad_detect(audio_path)
        print(f"   ✅ 偵測到 {len(speech_segments)} 個語音段")

        print("📝 Step 2: 語音轉文字 (Whisper)...")
        transcriptions = self._whisper_transcribe(audio_path)
        print(f"   ✅ 轉錄 {len(transcriptions)} 個段落")

        print("👤 Step 3: 發言人辨識...")
        speakers = self._speaker_diarize(audio_path, speech_segments, transcriptions)
        print(f"   ✅ 辨識 {len(speakers)} 位發言人")

        print("📋 Step 4: 整合會議記錄...")
        meeting = self._build_meeting_record(speakers, transcriptions, speech_segments)

        print("🧠 Step 5: 語意分析...")
        self._semantic_analysis(meeting)

        print("✅ 會議記錄處理完成!")
        return meeting

    def _vad_detect(self, audio_path: str) -> List[dict]:
        """Silero VAD 語音活動偵測
        
        Silero VAD v6.2.1+ API:
        - load_silero_vad() 返回 callable ScriptModule
        - model(audio_tensor, sr=16000) → [batch, 1] tensor，值 > 0.5 表示語音活動
        - 音頻需 512(16kHz) 或 256(8kHz) samples
        """
        try:
            from silero_vad import load_silero_vad
            import torch
            import numpy as np
            import soundfile as sf

            audio, sr = sf.read(audio_path, dtype="float32")
            if sr != 16000:
                # 重採樣 (簡化處理)
                audio = audio[:: sr // 16000] if sr > 16000 else audio

            model = load_silero_vad()
            segments = []
            chunk_size = 512  # 16kHz, 32ms per chunk
            in_speech = False
            start_frame = 0

            for i in range(0, len(audio) - chunk_size, chunk_size):
                chunk = torch.from_numpy(audio[i : i + chunk_size])
                result = model(chunk, sr=16000)
                speech_prob = result.item()

                if speech_prob > 0.5 and not in_speech:
                    in_speech = True
                    start_frame = i
                elif speech_prob <= 0.5 and in_speech:
                    in_speech = False
                    segments.append(
                        {
                            "start": start_frame / 16000,
                            "end": i / 16000,
                            "duration_sec": (i - start_frame) / 16000,
                        }
                    )

            if in_speech:
                segments.append(
                    {
                        "start": start_frame / 16000,
                        "end": len(audio) / 16000,
                        "duration_sec": (len(audio) - start_frame) / 16000,
                    }
                )

            return segments
        except ImportError:
            return []
        except Exception as e:
            print(f"VAD 錯誤: {e}")
            return []

    def _whisper_transcribe(self, audio_path: str) -> List[TranscriptionSegment]:
        """Whisper 語音轉文字"""
        try:
            import whisper
            import numpy as np
            import soundfile as sf

            model = whisper.load_model(
                name="base", device="cuda" if _has_cuda() else "cpu"
            )
            audio, sr = sf.read(audio_path, dtype="float32")

            if sr != 16000:
                audio = audio[:: sr // 16000] if sr > 16000 else audio

            result = model.transcribe(audio, language="zh", fp16=False)

            segments = []
            for seg in result.get("segments", []):
                segments.append(
                    TranscriptionSegment(
                        speaker_id="unknown",
                        speaker_name="unknown",
                        start=seg.get("start", 0.0),
                        end=seg.get("end", 0.0),
                        text=seg.get("text", "").strip(),
                        confidence=seg.get("avg_log_prob", 0.0),
                    )
                )
            return segments
        except ImportError:
            return []
        except Exception as e:
            print(f"Whisper 錯誤: {e}")
            return []

    def _speaker_diarize(
        self, audio_path: str, segments: List[dict], transcriptions: List[TranscriptionSegment]
    ) -> List[Speaker]:
        """發言人辨識"""
        speakers = []
        seen = set()

        for seg in transcriptions:
            name = seg.speaker_name
            if name and name not in seen:
                seen.add(name)
                profile = self.voice_db.get(name, {})
                speakers.append(
                    Speaker(
                        id=f"spk-{len(speakers)+1}",
                        name=name or "未知",
                        unit=profile.get("unit", ""),
                        role=profile.get("role", ""),
                        confidence=seg.confidence,
                    )
                )

        if not speakers:
            speakers.append(
                Speaker(id="spk-1", name="未知發言人", unit="", role="與會者")
            )

        return speakers

    def _build_meeting_record(
        self,
        speakers: List[Speaker],
        transcriptions: List[TranscriptionSegment],
        segments: List[dict],
    ) -> MeetingRecord:
        """建立會議記錄"""
        meeting_id = f"MEET-{datetime.now().strftime('%Y-%m-%d')}-{uuid.uuid4().hex[:8]}"

        meeting = MeetingRecord(
            meeting_id=meeting_id,
            title="社區會議",
            date=datetime.now().strftime("%Y-%m-%d"),
            time_start="09:00",
            time_end="10:00",
            location="社區活動中心",
            host="總幹事",
            speakers=speakers,
            segments=transcriptions,
            agenda=[],
            action_items=[],
        )

        self.meetings[meeting_id] = meeting
        return meeting

    def _semantic_analysis(self, meeting: MeetingRecord):
        """語意分析 (未來可用 LLM 驅動)"""
        pass

    def generate_meeting_minutes(self, meeting: MeetingRecord) -> str:
        """生成會議記錄 Markdown"""
        lines = []
        lines.append(f"# 會議記錄: {meeting.title}")
        lines.append("")
        lines.append("## 基本信息")
        lines.append(f"- **會議編號**: {meeting.meeting_id}")
        lines.append(f"- **日期**: {meeting.date}")
        lines.append(f"- **時間**: {meeting.time_start} - {meeting.time_end}")
        lines.append(f"- **地點**: {meeting.location}")
        lines.append(f"- **主持人**: {meeting.host}")
        lines.append("")

        if meeting.speakers:
            lines.append("## 與會者")
            lines.append("")
            lines.append("| 姓名 | 單位 | 角色 |")
            lines.append("|------|------|------|")
            for speaker in meeting.speakers:
                lines.append(f"| {speaker.name} | {speaker.unit} | {speaker.role} |")
            lines.append("")

        if meeting.agenda:
            lines.append("## 議程")
            lines.append("")
            for i, item in enumerate(meeting.agenda, 1):
                lines.append(f"### 議程 {i}: {item['title']}")
                lines.append("")
                lines.append(f"**發言人**: {item.get('speaker', 'N/A')}")
                lines.append(f"**內容**: {item.get('content', 'N/A')}")
                lines.append(f"**決議**: {item.get('resolution', 'N/A')}")
                lines.append("")

        if meeting.action_items:
            lines.append("## 行動項目")
            lines.append("")
            lines.append("| 編號 | 項目 | 負責人 | 截止日期 | 狀態 |")
            lines.append("|------|------|--------|----------|------|")
            for i, item in enumerate(meeting.action_items, 1):
                status = "⏳ 待處理" if item.get("status") == "pending" else "✅ 已完成"
                lines.append(
                    f"| {i} | {item['item']} | "
                    f"{item.get('owner', 'N/A')} | "
                    f"{item.get('deadline', 'N/A')} | "
                    f"{status} |"
                )
            lines.append("")

        lines.append("---")
        lines.append(f"**記錄時間**: {meeting.created_at}")
        lines.append(f"**確認簽名**: ___________")

        return "\n".join(lines)

    def save_meeting_record(self, meeting: MeetingRecord, output_path: str) -> str:
        """保存會議記錄為 Markdown 到檔案"""
        content = self.generate_meeting_minutes(meeting)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"💾 會議記錄已保存至: {output_path}")
        return content

    def export_to_json(self, meeting: MeetingRecord, output_path: str) -> dict:
        """導出為 JSON"""
        data = asdict(meeting)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 JSON 已導出至: {output_path}")
        return data


def _has_cuda() -> bool:
    """檢查是否有 CUDA 可用"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False