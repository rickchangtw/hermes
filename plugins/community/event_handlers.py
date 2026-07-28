"""
Event Handlers - 事件處理器

Handles incoming events from LINE/Telegram platforms and routes them to the
appropriate 7-Agent system for processing.
"""

import sys
import os

# 確保 sys.path 正確
hermes_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hermes_path not in sys.path:
    sys.path.insert(0, hermes_path)

from typing import Dict, Any, Optional

# 導入 7-Agent 實現
from .property_impl import PropertyAgentImpl
from .security_impl import SecurityAgentImpl
from .fire_impl import FireAgentImpl
from .energy_impl import EnergyAgentImpl
from .notify_impl import NotifyAgentImpl
from .resident_impl import ResidentAgentImpl
from .admin_impl import AdminAgentImpl


class CommunityEventHandler:
    """社區系統事件處理器"""
    
    AGENT_MAPPING = {
        'property': PropertyAgentImpl,
        'security': SecurityAgentImpl,
        'fire': FireAgentImpl,
        'energy': EnergyAgentImpl,
        'notify': NotifyAgentImpl,
        'resident': ResidentAgentImpl,
        'admin': AdminAgentImpl,
    }
    
    def __init__(self, agents: Dict[str, Any] = None):
        """
        初始化事件處理器
        
        Args:
            agents: 7-Agent 實例字典
        """
        self.agents = agents or {}
    
    def register_agent(self, agent_name: str, agent_instance):
        """註冊代理"""
        self.agents[agent_name] = agent_instance
    
    def handle_message(self, message: Dict[str, Any]):
        """
        處理 incoming 消息
        
        Args:
            message: 消息對象，包含 event_type, text, timestamp 等字段
        """
        text = message.get('text', '')
        
        # 路由到對應的 Agent
        for agent_name, agent_class in self.AGENT_MAPPING.items():
            if agent_name in self.agents:
                # 簡化路由邏輯：所有消息先通知所有 Agent
                agent = self.agents[agent_name]
                if hasattr(agent, 'on_message'):
                    try:
                        result = agent.on_message(message)
                        if result:
                            return result
                    except Exception as e:
                        print(f"[Event] {agent_name} 處理消息時發生錯誤：{e}")
        
        return None
    
    def handle_event(self, event: Dict[str, Any]):
        """
        處理 incoming 事件
        
        Args:
            event: 事件對象，包含 event_type, payload 等字段
        """
        payload = event.get('payload', {})
        event_type = payload.get('type', '')
        
        # 根據事件類型路由到對應的 Agent
        if event_type == 'property':
            if 'property' in self.agents:
                try:
                    self.agents['property'].on_event(event)
                except Exception as e:
                    print(f"[Event] Property Agent 處理事件時發生錯誤：{e}")
        
        elif event_type == 'security':
            if 'security' in self.agents:
                try:
                    self.agents['security'].on_event(event)
                except Exception as e:
                    print(f"[Event] Security Agent 處理事件時發生錯誤：{e}")
        
        elif event_type == 'fire':
            if 'fire' in self.agents:
                try:
                    self.agents['fire'].on_event(event)
                except Exception as e:
                    print(f"[Event] Fire Agent 處理事件時發生錯誤：{e}")
        
        elif event_type == 'energy':
            if 'energy' in self.agents:
                try:
                    self.agents['energy'].on_event(event)
                except Exception as e:
                    print(f"[Event] Energy Agent 處理事件時發生錯誤：{e}")
        
        elif event_type == 'notify':
            if 'notify' in self.agents:
                try:
                    self.agents['notify'].on_event(event)
                except Exception as e:
                    print(f"[Event] Notify Agent 處理事件時發生錯誤：{e}")
        
        elif event_type == 'resident':
            if 'resident' in self.agents:
                try:
                    self.agents['resident'].on_event(event)
                except Exception as e:
                    print(f"[Event] Resident Agent 處理事件時發生錯誤：{e}")
        
        elif event_type == 'admin':
            if 'admin' in self.agents:
                try:
                    self.agents['admin'].on_event(event)
                except Exception as e:
                    print(f"[Event] Admin Agent 處理事件時發生錯誤：{e}")
        
        return None
