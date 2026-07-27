"""
Agent Factory - 代理工廠

Factory for creating and managing the 7-Agent system instances.
"""

import sys
sys_path = '/home/rick/.hermes/hermes-agent'
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from core.hermes import HermesEventBus, HermesAgentRegistry, HermesState
from .adapter import CommunityAdapterImpl
from .property_impl import PropertyAgentImpl
from .security_impl import SecurityAgentImpl
from .fire_impl import FireAgentImpl
from .energy_impl import EnergyAgentImpl
from .notify_impl import NotifyAgentImpl
from .resident_impl import ResidentAgentImpl
from .admin_impl import AdminAgentImpl


class AgentFactory:
    """代理工廠"""
    
    def __init__(self, event_bus: HermesEventBus = None, 
                 agent_registry: HermesAgentRegistry = None,
                 shared_state: HermesState = None):
        """
        初始化代理工廠
        
        Args:
            event_bus: HermesEventBus 事件總線
            agent_registry: HermesAgentRegistry Agent 註冊表
            shared_state: HermesState 共享狀態
        """
        self.event_bus = event_bus
        self.agent_registry = agent_registry
        self.shared_state = shared_state
        self.agents = {}
    
    def create_all_agents(self):
        """創建所有代理"""
        # Property Agent
        self.agents['property'] = PropertyAgentImpl()
        
        # Security Agent
        self.agents['security'] = SecurityAgentImpl()
        
        # Fire Agent
        self.agents['fire'] = FireAgentImpl()
        
        # Energy Agent
        self.agents['energy'] = EnergyAgentImpl()
        
        # Notify Agent
        self.agents['notify'] = NotifyAgentImpl()
        
        # Resident Agent
        self.agents['resident'] = ResidentAgentImpl()
        
        # Admin Agent
        self.agents['admin'] = AdminAgentImpl()
        
        return self.agents
    
    def get_agent(self, agent_name: str):
        """獲取特定代理"""
        return self.agents.get(agent_name)
    
    def register_agent(self, agent_name: str, agent_instance):
        """註冊代理"""
        self.agents[agent_name] = agent_instance
        if self.agent_registry:
            self.agent_registry.register_agent(agent_name, agent_instance)
        return agent_instance
