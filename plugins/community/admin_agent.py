"""
Admin Agent 介面 - Admin Agent Interface
"""

from abc import ABC, abstractmethod

class AdminAgent(ABC):
    """Admin Agent 介面"""
    
    @abstractmethod
    def on_admin_event(self, event):
        """處理管理員事件"""
        ...
