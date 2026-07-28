"""
Property Agent 介面 - Property Agent Interface
"""

from abc import ABC, abstractmethod

class PropertyAgent(ABC):
    """Property Agent 介面"""
    
    @abstractmethod
    def on_property_event(self, event):
        """處理物業事件"""
        ...
