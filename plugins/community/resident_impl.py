"""
Resident Agent 實現 - Resident Agent Implementation
"""

from .resident_agent import ResidentAgent

class ResidentAgentImpl(ResidentAgent):
    """Resident Agent 實現"""
    
    def on_resident_event(self, event):
        """處理居民通訊事件"""
        text = event.get('text')
        if text:
            print(f"[Resident] 收到事件：{text}")
        return None
