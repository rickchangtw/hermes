"""
Fire Agent 介面 - Fire Agent Interface
"""

from abc import ABC, abstractmethod

class FireAgent(ABC):
    """Fire Agent 介面"""
    
    @abstractmethod
    def on_fire_event(self, event):
        """處理火災事件"""
        ...
