"""
Community Platform Adapter - 社區系統適配器

Integrates the 600-household smart community management system (7-Agent:
admin, property, security, fire, energy, notify, resident) with Hermes Agent
for event-driven multi-agent operation.
"""

import sys
sys_path_base = '/home/rick/.hermes/hermes-agent'
if sys_path_base not in sys.path:
    sys.path.insert(0, sys_path_base)

from typing import Dict, Any, Optional, List
import json
import os

# 導入核心 Hermes 模組
from core.hermes import HermesAdapter, HermesEventBus, HermesOrchestrator, HermesAgentRegistry
from core.hermes.shared_state import SharedState

# 導入 7-Agent 實現 - 使用絕對導入
from .property_impl import PropertyAgentImpl
from .security_impl import SecurityAgentImpl
from .fire_impl import FireAgentImpl
from .energy_impl import EnergyAgentImpl
from .notify_impl import NotifyAgentImpl
from .resident_impl import ResidentAgentImpl
from .admin_impl import AdminAgentImpl


class CommunityAdapterImpl(HermesAdapter):
    """社區適配器實現 - 7-Agent 整合"""
    
    def __init__(self, 
                 event_bus: HermesEventBus = None,
                 agent_registry: HermesAgentRegistry = None,
                 shared_state: SharedState = None,
                 orchestrator: HermesOrchestrator = None):
        """
        初始化社區適配器
        
        Args:
            event_bus: HermesEventBus 事件總線
            agent_registry: HermesAgentRegistry Agent 註冊表
            shared_state: SharedState 共享狀態
            orchestrator: HermesOrchestrator 調度器
        """
        self.event_bus = event_bus
        self.agent_registry = agent_registry
        self.shared_state = shared_state
        self.orchestrator = orchestrator
        self.agents = {}
        self.event_handler = None
        
        # 創建並註冊 7-Agent
        self._create_all_agents()
    
    def _create_all_agents(self):
        """創建所有 7-Agent 並註冊到 Hermes"""
        
        # Property Agent - 物業管理
        self.agents['property'] = PropertyAgentImpl()
        
        # Security Agent - 安全管理
        self.agents['security'] = SecurityAgentImpl()
        
        # Fire Agent - 火災安全
        self.agents['fire'] = FireAgentImpl()
        
        # Energy Agent - 能源管理
        self.agents['energy'] = EnergyAgentImpl()
        
        # Notify Agent - 通知管理
        self.agents['notify'] = NotifyAgentImpl()
        
        # Resident Agent - 居民通訊
        self.agents['resident'] = ResidentAgentImpl()
        
        # Admin Agent - 管理員管理
        self.agents['admin'] = AdminAgentImpl()
        
        # 創建事件處理器
        self.event_handler = self._create_event_handler()
    
    def _create_event_handler(self) -> Any:
        """創建事件處理器"""
        
        from .event_handlers import CommunityEventHandler
        
        handler = CommunityEventHandler(self.agents)
        
        # 註冊所有 Agent
        for agent_name, agent_instance in self.agents.items():
            handler.register_agent(agent_name, agent_instance)
        
        return handler
    
    def on_message(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        處理 incoming 消息
        
        Args:
            event: 事件對象，包含 event_type, text, timestamp 等字段
        
        Returns:
            處理結果，或 None
        """
        result = None
        if self.event_handler:
            result = self.event_handler.handle_message(event)
        else:
            # 簡化處理：打印消息
            text = event.get('text', '')
            if text:
                print(f"[Community] 收到消息：{text}")
        
        return result
    
    def on_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        處理 incoming 事件
        
        Args:
            event: 事件對象，包含 event_type, payload 等字段
        
        Returns:
            處理結果，或 None
        """
        result = None
        if self.event_handler:
            result = self.event_handler.handle_event(event)
        else:
            # 簡化處理：打印事件
            payload = event.get('payload', {})
            event_type = payload.get('type', '')
            print(f"[Community] 收到事件類型：{event_type}")
        
        return result


# 便捷函數
def _build_adapter() -> CommunityAdapterImpl:
    """
    創建社區適配器實例
    
    Returns:
        CommunityAdapterImpl 實例
    """
    return CommunityAdapterImpl()

# 類型別名 - CommunityAdapter 等同 CommunityAdapterImpl
CommunityAdapter = CommunityAdapterImpl

# 導出
__all__ = [
    'CommunityAdapter',
    'CommunityAdapterImpl',
    '_build_adapter',
]
