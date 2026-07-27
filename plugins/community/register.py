"""
Community Platform Registration - 社區系統註冊

Registers the Community Platform (7-Agent system) with the Hermes Gateway.
"""

# 創建社區系統適配器
def _build_adapter(event_bus=None, agent_registry=None, shared_state=None):
    """創建社區系統適配器"""
    from .adapter import CommunityAdapterImpl
    return CommunityAdapterImpl(event_bus, agent_registry, shared_state)

# 檢查社區系統需求
def _check_community_requirements():
    """檢查社區系統需求"""
    # 檢查必要的依賴
    return True

# 檢查社區系統是否已連接
def _is_connected(adapter):
    """檢查社區系統是否已連接"""
    # 暫時返回 True，實際實現需要檢查 API 連接狀態
    return True

# 獨立發送函數
def _standalone_send(event):
    """獨立發送消息"""
    text = event.get('text')
    if text:
        print(f"[Community Standalone] 發送消息：{text}")
    return True

# 應用 YAML 配置
def _apply_yaml_config(config):
    """應用 YAML 配置"""
    return config

# 交互式設置
def interactive_setup():
    """交互式設置"""
    print("[Community] 社區系統設置...")
    return {}

# 適配器類型
ADAPTER_TYPE = "Community"

# 檢查函數
CHECK_FN = _check_community_requirements

# 連接檢查函數
IS_CONNECTED = _is_connected

# 創建適配器函數
ADAPTER_FACTORY = _build_adapter

# 交互式設置
SETUP_FN = interactive_setup

# 應用 YAML 配置
APPLY_YAML_CONFIG_FN = _apply_yaml_config

# 獨立發送函數
STANDALONE_SENDER_FN = _standalone_send

# 最大消息長度
MAX_MESSAGE_LENGTH = 4096

# Emoji
EMOJI = "🏠"

# 允許更新命令
ALLOW_UPDATE_COMMAND = True

# 允許更新環境變量
ALLOWED_USERS_ENV = "COMMUNITY_ALLOWED_USERS"

# 允許所有用戶環境變量
ALLOW_ALL_ENV = "COMMUNITY_ALLOW_ALL_USERS"

# 時區環境變量
TIMEZONE_ENV = "COMMUNITY_TIMEZONE"

# 時區偏移環境變量
TIMEZONE_OFFSET_ENV = "COMMUNITY_TIMEZONE_OFFSET"

# 家庭通道環境變量
HOME_CHANNEL_ENV = "COMMUNITY_HOME_CHANNEL"

# 創建適配器環境變量
CREATE_ADAPTER_ENV = "COMMUNITY_CREATE_ADAPTER"
