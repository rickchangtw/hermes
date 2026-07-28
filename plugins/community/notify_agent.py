"""
Notify Agent 介面 - Notify Agent Interface
"""

from abc import ABC, abstractmethod

class NotifyAgent(ABC):
    """Notify Agent 介面"""
    
    @abstractmethod
    def on_notify_event(self, event):
        """處理通知事件"""
        ...
