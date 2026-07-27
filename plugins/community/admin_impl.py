""""
Admin Agent 實現 - Admin Agent Implementation
"""

from .admin_agent import AdminAgent

class AdminAgentImpl(AdminAgent):
    """Admin Agent 實現"""

    def on_admin_event(self, event):
        """處理管理員事件"""
        text = event.get('text')
        if text:
            print(f"[Admin] 收到事件：{text}")
        return None
