"""
Energy Agent 介面 - Energy Agent Interface
"""

from abc import ABC, abstractmethod

class EnergyAgent(ABC):
    """Energy Agent 介面"""
    
    @abstractmethod
    def on_energy_event(self, event):
        """處理能源事件"""
        ...
