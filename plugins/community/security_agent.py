"""
Security Agent 介面 - Security Agent Interface
"""

from abc import ABC, abstractmethod

class SecurityAgent(ABC):
    """Security Agent 介面"""
    
    @abstractmethod
    def on_security_event(self, event):
        """處理安全事件"""
        ...
