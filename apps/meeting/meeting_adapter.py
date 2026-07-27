"""
Meeting Adapter 實現 - 會議記錄適配器實現
"""

from . import MeetingAdapter as MeetingAdapterBase


class MeetingAdapterImpl(MeetingAdapterBase):
    """會議記錄適配器實現"""
    
    def __init__(self, event_bus=None, agent_registry=None, shared_state=None):
        super().__init__(event_bus, agent_registry, shared_state)
    
    def on_message(self, event):
        """處理會議消息"""
        text = event.get('text', '')
        if text:
            print(f"[Meeting App] 會議消息：{text}")
        return True
    
    def on_event(self, event):
        """處理會議事件"""
        event_type = event.get('event_type', '')
        if event_type:
            print(f"[Meeting App] 會議事件：{event_type}")
        return True