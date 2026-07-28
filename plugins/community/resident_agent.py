"""
Resident Agent 介面 - Resident Agent Interface
"""

from abc import ABC, abstractmethod

class ResidentAgent(ABC):
    """Resident Agent 介面"""
    
    @abstractmethod
    def on_resident_event(self, event):
        """處理居民事件"""
        ...
