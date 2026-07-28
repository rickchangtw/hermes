"""
物業代理 - App 層 - Property App Agent
"""

from . import CommunityAdapter


class PropertyAppAgent:
    """物業代理 - App 層"""
    
    def __init__(self, event_bus=None, agent_registry=None, shared_state=None):
        self.event_bus = event_bus
        self.agent_registry = agent_registry
        self.shared_state = shared_state
        self.adapter = CommunityAdapter(event_bus, agent_registry, shared_state)
    
    def on_message(self, event):
        """處理 Property 消息"""
        text = event.get('text', '')
        if text:
            print(f"[Property App] 收到消息：{text}")
        return True
    
    def on_event(self, event):
        """處理 Property 事件"""
        event_type = event.get('event_type', '')
        if event_type:
            print(f"[Property App] 收到事件：{event_type}")
        return True
