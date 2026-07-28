"""
Community App Adapter - 社區系統應用層適配器實現
"""

from . import CommunityAdapter as CommunityAdapterBase


class CommunityAdapterImpl(CommunityAdapterBase):
    """社區系統適配器實現"""
    
    def __init__(self, event_bus=None, agent_registry=None, shared_state=None):
        super().__init__(event_bus, agent_registry, shared_state)
    
    def on_message(self, event):
        """處理社區消息"""
        text = event.get('text', '')
        if text:
            print(f"[Community App] 收到消息：{text}")
        
        # 委託給 plugins/community 處理
        if self.event_handler:
            return self.event_handler.handle_message(event)
        return True
    
    def on_event(self, event):
        """處理社區事件"""
        event_type = event.get('event_type', '')
        if event_type:
            print(f"[Community App] 收到事件：{event_type}")
        
        if self.event_handler:
            return self.event_handler.handle_event(event)
        return True