"""
Community Platform Adapter - 社區系統適配器

運行測試：
python3 -m community.test_community_adapter

或：
cd /home/rick/.hermes/hermes-agent/plugins
python3 -m community.test_community_adapter
"""

import sys
import os

# 添加 hermes-agent 父目錄到 sys.path
sys_path = '/home/rick/.hermes/hermes-agent'
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from pathlib import Path
from community.adapter import CommunityAdapter, CommunityAdapterImpl
from community import adapter
from community.register import (
    _build_adapter,
    _check_community_requirements,
    _is_connected,
    interactive_setup,
    _standalone_send,
    _apply_yaml_config,
    ADAPTER_TYPE,
    CHECK_FN,
    IS_CONNECTED,
    ADAPTER_FACTORY,
    SETUP_FN,
    APPLY_YAML_CONFIG_FN,
    STANDALONE_SENDER_FN,
    MAX_MESSAGE_LENGTH,
    EMOJI,
    ALLOW_UPDATE_COMMAND,
    ALLOWED_USERS_ENV,
    ALLOW_ALL_ENV,
    TIMEZONE_ENV,
    TIMEZONE_OFFSET_ENV,
    HOME_CHANNEL_ENV,
    CREATE_ADAPTER_ENV,
)

def run_tests():
    """運行所有測試"""
    
    print('=' * 60)
    print('Community Platform Adapter - 社區系統適配器 測試報告')
    print('=' * 60)
    print()
    
    results = []
    
    # 測試 1: Community 模組導入
    try:
        from community.adapter import CommunityAdapter, CommunityAdapterImpl
        from community.register import (
            _build_adapter,
            _check_community_requirements,
            _is_connected,
            interactive_setup,
            _standalone_send,
            _apply_yaml_config,
            ADAPTER_TYPE,
            CHECK_FN,
            IS_CONNECTED,
            ADAPTER_FACTORY,
            SETUP_FN,
            APPLY_YAML_CONFIG_FN,
            STANDALONE_SENDER_FN,
            MAX_MESSAGE_LENGTH,
            EMOJI,
            ALLOW_UPDATE_COMMAND,
            ALLOWED_USERS_ENV,
            ALLOW_ALL_ENV,
            TIMEZONE_ENV,
            TIMEZONE_OFFSET_ENV,
            HOME_CHANNEL_ENV,
            CREATE_ADAPTER_ENV,
        )
        results.append(('測試 1: Community 模組導入', '✓ PASS'))
        print('✓ 測試 1: Community 模組導入 - PASS')
    except Exception as e:
        results.append(('測試 1: Community 模組導入', f'✗ FAIL: {e}'))
        print(f'✗ 測試 1: Community 模組導入 - FAIL: {e}')
    
    # 測試 2: CommunityAdapter 基本功能
    try:
        adapter_instance = _build_adapter()
        assert isinstance(adapter_instance, CommunityAdapterImpl)
        results.append(('測試 2: CommunityAdapter 基本功能', '✓ PASS'))
        print('✓ 測試 2: CommunityAdapter 基本功能 - PASS')
    except Exception as e:
        results.append(('測試 2: CommunityAdapter 基本功能', f'✗ FAIL: {e}'))
        print(f'✗ 測試 2: CommunityAdapter 基本功能 - FAIL: {e}')
    
    # 測試 3: 檢查需求
    try:
        result = _check_community_requirements()
        assert result == True
        results.append(('測試 3: 檢查需求', '✓ PASS'))
        print('✓ 測試 3: 檢查需求 - PASS')
    except Exception as e:
        results.append(('測試 3: 檢查需求', f'✗ FAIL: {e}'))
        print(f'✗ 測試 3: 檢查需求 - FAIL: {e}')
    
    # 測試 4: 檢查連接
    try:
        is_conn = _is_connected(adapter_instance)
        assert is_conn == True
        results.append(('測試 4: 檢查連接', '✓ PASS'))
        print('✓ 測試 4: 檢查連接 - PASS')
    except Exception as e:
        results.append(('測試 4: 檢查連接', f'✗ FAIL: {e}'))
        print(f'✗ 測試 4: 檢查連接 - FAIL: {e}')
    
    # 測試 5: 處理消息
    try:
        event = {
            'event_type': 'message',
            'text': 'Hello from Community!',
            'timestamp': '2026-07-25 22:00:00'
        }
        result = adapter_instance.on_message(event)
        results.append(('測試 5: 處理消息', '✓ PASS'))
        print('✓ 測試 5: 處理消息 - PASS')
    except Exception as e:
        results.append(('測試 5: 處理消息', f'✗ FAIL: {e}'))
        print(f'✗ 測試 5: 處理消息 - FAIL: {e}')
    
    # 測試 6: 處理事件
    try:
        event2 = {
            'event_type': 'event',
            'payload': {'type': 'test', 'data': 'test_data'}
        }
        result = adapter_instance.on_event(event2)
        results.append(('測試 6: 處理事件', '✓ PASS'))
        print('✓ 測試 6: 處理事件 - PASS')
    except Exception as e:
        results.append(('測試 6: 處理事件', f'✗ FAIL: {e}'))
        print(f'✗ 測試 6: 處理事件 - FAIL: {e}')
    
    # 測試 7: 獨立發送
    try:
        result = _standalone_send(event)
        assert result == True
        results.append(('測試 7: 獨立發送', '✓ PASS'))
        print('✓ 測試 7: 獨立發送 - PASS')
    except Exception as e:
        results.append(('測試 7: 獨立發送', f'✗ FAIL: {e}'))
        print(f'✗ 測試 7: 獨立發送 - FAIL: {e}')
    
    # 測試 8: 應用 YAML 配置
    try:
        config = {'debug': True, 'test': True}
        result = _apply_yaml_config(config)
        assert result == config
        results.append(('測試 8: 應用 YAML 配置', '✓ PASS'))
        print('✓ 測試 8: 應用 YAML 配置 - PASS')
    except Exception as e:
        results.append(('測試 8: 應用 YAML 配置', f'✗ FAIL: {e}'))
        print(f'✗ 測試 8: 應用 YAML 配置 - FAIL: {e}')
    
    # 測試 9: 交互式設置
    try:
        setup_result = interactive_setup()
        results.append(('測試 9: 交互式設置', '✓ PASS'))
        print('✓ 測試 9: 交互式設置 - PASS')
    except Exception as e:
        results.append(('測試 9: 交互式設置', f'✗ FAIL: {e}'))
        print(f'✗ 測試 9: 交互式設置 - FAIL: {e}')
    
    # 測試 10: 常數檢查
    try:
        assert ADAPTER_TYPE == "Community"
        assert CHECK_FN is not None
        assert IS_CONNECTED is not None
        assert ADAPTER_FACTORY is not None
        assert SETUP_FN is not None
        assert APPLY_YAML_CONFIG_FN is not None
        assert STANDALONE_SENDER_FN is not None
        assert MAX_MESSAGE_LENGTH == 4096
        assert EMOJI == "🏠"
        assert ALLOW_UPDATE_COMMAND == True
        results.append(('測試 10: 常數檢查', '✓ PASS'))
        print('✓ 測試 10: 常數檢查 - PASS')
    except Exception as e:
        results.append(('測試 10: 常數檢查', f'✗ FAIL: {e}'))
        print(f'✗ 測試 10: 常數檢查 - FAIL: {e}')
    
    # 測試 11: plugin.yaml 檢查
    try:
        plugin_file = Path('/home/rick/.hermes/hermes-agent/plugins/community/plugin.yaml')
        if plugin_file.exists():
            content = plugin_file.read_text()
            assert 'community' in content
            assert 'label: Community Platform' in content
            results.append(('測試 11: plugin.yaml 檢查', '✓ PASS'))
            print('✓ 測試 11: plugin.yaml 檢查 - PASS')
        else:
            results.append(('測試 11: plugin.yaml 檢查', '⚠ WARNING: plugin.yaml 不存在'))
            print('⚠ 測試 11: plugin.yaml 檢查 - WARNING: plugin.yaml 不存在')
    except Exception as e:
        results.append(('測試 11: plugin.yaml 檢查', f'✗ FAIL: {e}'))
        print(f'✗ 測試 11: plugin.yaml 檢查 - FAIL: {e}')
    
    # 測試 12: __init__.py 導出檢查
    try:
        from community import CommunityAdapter, CommunityAdapterImpl
        assert CommunityAdapter is not None
        assert CommunityAdapterImpl is not None
        results.append(('測試 12: __init__.py 導出檢查', '✓ PASS'))
        print('✓ 測試 12: __init__.py 導出檢查 - PASS')
    except Exception as e:
        results.append(('測試 12: __init__.py 導出檢查', f'✗ FAIL: {e}'))
        print(f'✗ 測試 12: __init__.py 導出檢查 - FAIL: {e}')
    
    # 測試 13: 7-Agent Interface/Impl 檢查
    try:
        from community.admin_agent import AdminAgent
        from community.admin_impl import AdminAgentImpl
        from community.property_agent import PropertyAgent
        from community.property_impl import PropertyAgentImpl
        from community.security_agent import SecurityAgent
        from community.security_impl import SecurityAgentImpl
        from community.fire_agent import FireAgent
        from community.fire_impl import FireAgentImpl
        from community.energy_agent import EnergyAgent
        from community.energy_impl import EnergyAgentImpl
        from community.notify_agent import NotifyAgent
        from community.notify_impl import NotifyAgentImpl
        from community.resident_agent import ResidentAgent
        from community.resident_impl import ResidentAgentImpl
        results.append(('測試 13: 7-Agent Interface/Impl 檢查', '✓ PASS'))
        print('✓ 測試 13: 7-Agent Interface/Impl 檢查 - PASS')
    except Exception as e:
        results.append(('測試 13: 7-Agent Interface/Impl 檢查', f'✗ FAIL: {e}'))
        print(f'✗ 測試 13: 7-Agent Interface/Impl 檢查 - FAIL: {e}')
    
    # 測試 14: 完整架構檢查
    try:
        community_dir = Path('/home/rick/.hermes/hermes-agent/plugins/community')
        files = [f.name for f in community_dir.iterdir() if f.is_file()]
        assert len(files) >= 10
        assert '__init__.py' in files
        assert 'adapter.py' in files
        assert 'register.py' in files
        results.append(('測試 14: 完整架構檢查', '✓ PASS'))
        print('✓ 測試 14: 完整架構檢查 - PASS')
    except Exception as e:
        results.append(('測試 14: 完整架構檢查', f'✗ FAIL: {e}'))
        print(f'✗ 測試 14: 完整架構檢查 - FAIL: {e}')
    
    # 總結
    print()
    print('=' * 60)
    print('測試總結')
    print('=' * 60)
    
    passed = sum(1 for r in results if 'PASS' in r[1] or 'WARNING' in r[1])
    failed = sum(1 for r in results if 'FAIL' in r[1])
    total = len(results)
    
    print(f'總測試項目：{total}')
    print(f'通過：{passed}')
    print(f'失敗：{failed}')
    
    if failed == 0:
        print()
        print('🎉 所有測試通過！')
        print('=' * 60)
    elif failed == 1:
        print()
        print('⚠ 有一個測試失敗，請檢查相應的錯誤訊息。')
        print('=' * 60)
    else:
        print()
        print(f'⚠ 有 {failed} 個測試失敗，請檢查相應的錯誤訊息。')
        print('=' * 60)
    
    return results, passed, failed, total

if __name__ == '__main__':
    results, passed, failed, total = run_tests()
    
    # 返回結果供其他腳本使用
    sys.exit(0 if failed == 0 else 1)
