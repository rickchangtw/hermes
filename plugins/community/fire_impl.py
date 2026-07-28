"""
Fire Agent 實現 - Fire Agent Implementation
"""

from .fire_agent import FireAgent

class FireAgentImpl(FireAgent):
    """Fire Agent 實現"""
    
    def on_fire_event(self, event):
        """處理火災安全事件"""
        text = event.get('text')
        if text:
            print(f"[Fire] 收到事件：{text}")
        return None
