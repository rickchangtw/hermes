"""
Property Agent 實現 - Property Agent Implementation
"""

from .property_agent import PropertyAgent

class PropertyAgentImpl(PropertyAgent):
    """Property Agent 實現"""
    
    def on_property_event(self, event):
        """處理物業事件"""
        text = event.get('text')
        if text:
            print(f"[Property] 收到事件：{text}")
        return None
