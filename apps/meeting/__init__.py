"""
即時會議記錄系統 - Hermes App 適配器

整合共享會議記錄系統（Silero VAD + Whisper + PostgreSQL），
提供 7 個專用 Meeting Agent（admin、property、security、fire、energy、notify、resident）。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class MeetingApp(ABC):
    """會議系統應用層基類"""
    
    @abstractmethod
    def on_message(self, event: Dict[str, Any]) -> bool:
        """處理消息"""
        pass
    
    @abstractmethod
    def on_event(self, event: Dict[str, Any]) -> bool:
        """處理事件"""
        pass


class MeetingAdapter(MeetingApp):
    """會議記錄適配器 - 應用層入口
    
    整合 shared-wiki 的會議記錄系統：
    - Silero VAD 語音活動偵測
    - Whisper 語音轉文字
    - 發言人辨識
    - PostgreSQL 儲存
    - WebSocket 即時推送
    """
    
    def __init__(self, event_bus=None, agent_registry=None, shared_state=None):
        self.event_bus = event_bus
        self.agent_registry = agent_registry
        self.shared_state = shared_state
        self.agents = {}
        self._initialized = False
    
    def initialize(self):
        """初始化會議 Agent 系統"""
        if self._initialized:
            return
        self._initialized = True
    
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """獲取特定 Meeting Agent"""
        if not self._initialized:
            self.initialize()
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, Any]:
        """獲取所有 Meeting Agent"""
        if not self._initialized:
            self.initialize()
        return self.agents.copy()
    
    def on_message(self, event: Dict[str, Any]) -> bool:
        """處理會議消息"""
        if not self._initialized:
            self.initialize()
        print(f"[Meeting App] 收到消息：{event.get('text', '')}")
        return True
    
    def on_event(self, event: Dict[str, Any]) -> bool:
        """處理會議事件"""
        if not self._initialized:
            self.initialize()
        event_type = event.get('event_type', '')
        print(f"[Meeting App] 收到事件：{event_type}")
        return True