"""
Security Agent 實現 - Security Agent Implementation
"""

from .security_agent import SecurityAgent

class SecurityAgentImpl(SecurityAgent):
    """Security Agent 實現"""
    
    def on_security_event(self, event):
        """處理安全管理事件"""
        text = event.get('text')
        if text:
            print(f"[Security] 收到事件：{text}")
        return None
