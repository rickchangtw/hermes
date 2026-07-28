"""
Notify Agent 實現 - Notify Agent Implementation
"""

from .notify_agent import NotifyAgent

class NotifyAgentImpl(NotifyAgent):
    """Notify Agent 實現"""
    
    def on_notify_event(self, event):
        """處理通知管理事件"""
        text = event.get('text')
        if text:
            print(f"[Notify] 收到事件：{text}")
        return None
