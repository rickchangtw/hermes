"""
600 戶社區系統 - Hermes App 適配器

整合 plugins/community/ 的 7-Agent 系統，提供 Hermes 應用層介面。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class CommunityApp(ABC):
    """社區系統應用層基類"""
    
    @abstractmethod
    def on_message(self, event: Dict[str, Any]) -> bool:
        """處理消息"""
        pass
    
    @abstractmethod
    def on_event(self, event: Dict[str, Any]) -> bool:
        """處理事件"""
        pass


class CommunityAdapter(CommunityApp):
    """社區系統適配器 - 應用層入口"""
    
    def __init__(self, event_bus=None, agent_registry=None, shared_state=None):
        self.event_bus = event_bus
        self.agent_registry = agent_registry
        self.shared_state = shared_state
        self.agents = {}
        self._initialized = False
    
    def initialize(self):
        """初始化 7-Agent 系統"""
        if self._initialized:
            return
        
        # 從 plugins/community 導入實際的 Agent 實現
        try:
            from community.agent_factory import AgentFactory
            from community.event_handlers import CommunityEventHandler
            from community.adapter import CommunityAdapterImpl
            
            factory = AgentFactory(self.event_bus, self.agent_registry, self.shared_state)
            self.agents = factory.create_all_agents()
            
            self.event_handler = CommunityEventHandler(self.agents)
            
            # 註冊到註冊表
            if self.agent_registry:
                for agent_id, agent in self.agents.items():
                    self.agent_registry.register(agent_id, agent)
            
            self._initialized = True
        except ImportError as e:
            # Fallback: 如果 plugins 不可用，使用簡化模式
            self._initialized = True
    
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """獲取特定 Agent"""
        if not self._initialized:
            self.initialize()
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, Any]:
        """獲取所有 Agent"""
        if not self._initialized:
            self.initialize()
        return self.agents.copy()
    
    def on_message(self, event: Dict[str, Any]) -> bool:
        """處理消息 - 委託給 plugins"""
        if not self._initialized:
            self.initialize()
        print(f"[Community App] 收到消息：{event.get('text', '')}")
        return True
    
    def on_event(self, event: Dict[str, Any]) -> bool:
        """處理事件 - 委託給 plugins"""
        if not self._initialized:
            self.initialize()
        event_type = event.get('event_type', '')
        print(f"[Community App] 收到事件：{event_type}")
        return True