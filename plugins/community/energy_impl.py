"""
Energy Agent 實現 - Energy Agent Implementation
"""

from .energy_agent import EnergyAgent

class EnergyAgentImpl(EnergyAgent):
    """Energy Agent 實現"""
    
    def on_energy_event(self, event):
        """處理能源管理事件"""
        text = event.get('text')
        if text:
            print(f"[Energy] 收到事件：{text}")
        return None
