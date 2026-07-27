"""
Community 模組導出

從 adapter 模組導出 CommunityAdapter 和 CommunityAdapterImpl。
"""

import sys
import os

# 確保 sys.path 正確 - 添加 plugins 目錄到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
plugins_dir = os.path.dirname(current_dir)
if plugins_dir not in sys.path:
    sys.path.insert(0, plugins_dir)

# 使用絕對導入
from community.adapter import CommunityAdapter, CommunityAdapterImpl

# 導出
__all__ = [
    "CommunityAdapter",
    "CommunityAdapterImpl",
]
