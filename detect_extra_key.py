"""
检测额外按键的系统功能
用途：识别MK850键盘上索引85位置（左Shift和Z之间）的额外按键在系统中的实际功能
"""

import time
import sys

def detect_key_function():
    """检测按键的系统功能"""
    try:
        import keyboard
        
        print("=" * 70)
        print("额外按键功能检测器")
        print("=" * 70)
        print("\n📌 检测目标：索引85位置的额外按键（左Shift和Z之间）")
        print("\n🔍 检测方法：")
        print("   1. 按下该按键，查看系统识别的功能")
        print("   2. 观察是否触发特殊功能或组合键")
        print("   3. 记录扫描码、虚拟键码和按键名称")
        print("\n💡 提示：")
        print("   - 单独按下该按键")
        print("   - 尝试与其他键组合（如Ctrl+该键、Alt+该键等）")
        print("   - 按 Ctrl+C 退出\n")
        print("-" * 70)
        
        detected_info = []
        
        def on_key_event(event):
            if event.event_type == 'down':
                key_info = {
                    'name': event.name,
                    'scan_code': event.scan_code,
                    'time': time.strftime('%H:%M:%S')
                }
                
                # 获取更多信息
                try:
                    # 尝试获取虚拟键码
                    vk_code = None
                    if hasattr(event, 'vk'):
                        vk_code = event.vk
                    
                    info_str = (
                        f"[{key_info['time']}] ⬇️  按下 | "
                        f"扫描码: {key_info['scan_code']:3d} (0x{key_info['scan_code']:02X}) | "
                        f"按键名: {key_info['name']:15s}"
                    )
                    
                    if vk_code:
                        info_str += f" | 虚拟键码: {vk_code:3d} (0x{vk_code:02X})"
                    
                    print(info_str)
                    
                    # 记录检测结果
                    detected_info.append(key_info)
                    
                    # 检查是否是目标按键（扫描码86）
                    if key_info['scan_code'] == 86:
                        print("\n" + "=" * 70)
                        print("✅ 检测到目标按键！")
                        print("=" * 70)
                        print(f"扫描码: {key_info['scan_code']} (0x{key_info['scan_code']:02X})")
                        print(f"按键名: {key_info['name']}")
                        if vk_code:
                            print(f"虚拟键码: {vk_code} (0x{vk_code:02X})")
                        
                        # 分析按键功能
                        analyze_key_function(key_info['name'], vk_code)
                        print("=" * 70 + "\n")
                        
                except Exception as e:
                    print(f"[{key_info['time']}] ⬇️  按下 | "
                          f"扫描码: {key_info['scan_code']:3d} | "
                          f"按键名: {key_info['name']:15s} | "
                          f"错误: {e}")
        
        # 注册监听器
        keyboard.hook(on_key_event)
        
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            print("\n" + "-" * 70)
            print(f"\n✅ 检测结束，共检测到 {len(detected_info)} 次按键事件")
            
            if detected_info:
                print("\n📊 检测结果汇总：")
                unique_scancodes = set()
                for info in detected_info:
                    unique_scancodes.add(info['scan_code'])
                
                print(f"\n检测到的不同扫描码：")
                for code in sorted(unique_scancodes):
                    count = sum(1 for i in detected_info if i['scan_code'] == code)
                    names = set(i['name'] for i in detected_info if i['scan_code'] == code)
                    print(f"  扫描码 {code:3d} (0x{code:02X}): 出现{count}次, 按键名: {', '.join(names)}")
            
            return True
            
    except ImportError:
        print("❌ keyboard 库未安装")
        print("   请运行: pip install keyboard")
        return False
    except Exception as e:
        print(f"❌ 检测失败: {e}")
        return False


def analyze_key_function(key_name, vk_code):
    """分析按键的可能功能"""
    print("\n🔍 功能分析：")
    
    # 根据按键名称分析
    common_keys = {
        'oem_102': 'ISO布局额外键（通常在左Shift右边）',
        'non_us_backslash': '非美式反斜杠键（ISO标准）',
        'backslash': '标准反斜杠键',
        'grave': '重音符键 (`)',
        'tab': 'Tab键',
        'caps_lock': 'Caps Lock键',
        'shift': 'Shift键',
        'ctrl': 'Ctrl键',
        'alt': 'Alt键',
    }
    
    if key_name in common_keys:
        print(f"   📌 按键类型: {common_keys[key_name]}")
    else:
        print(f"   📌 按键类型: 未知/特殊按键 ({key_name})")
    
    # 根据虚拟键码分析
    if vk_code:
        vk_functions = {
            0xE0: 'VK_OEM_102 - ISO布局额外键',
            0xDC: 'VK_OEM_5 - 反斜杠/竖线键',
            0xC0: 'VK_OEM_3 - 重音符/波浪号键',
            0x09: 'VK_TAB - Tab键',
            0x14: 'VK_CAPITAL - Caps Lock键',
            0x10: 'VK_SHIFT - Shift键',
            0x11: 'VK_CONTROL - Ctrl键',
            0x12: 'VK_MENU - Alt键',
        }
        
        vk_hex = f"0x{vk_code:02X}"
        if vk_hex in vk_functions:
            print(f"   📌 Windows VK: {vk_functions[vk_hex]}")
        else:
            print(f"   📌 Windows VK: 0x{vk_code:02X} (自定义/特殊)")
    
    # 给出建议
    print("\n💡 建议命名：")
    if key_name in ['oem_102', 'non_us_backslash']:
        print("   ✅ 推荐: ISO_EXTRA 或 EXTRA_KEY")
        print("   📝 说明: 这是ISO布局键盘的标准额外按键")
    elif key_name == 'backslash':
        print("   ✅ 推荐: BACKSLASH_EXTRA 或 SLASH_VERTICAL")
        print("   📝 说明: 额外的反斜杠/竖线键")
    else:
        print(f"   ✅ 推荐: EXTRA_KEY_{key_name.upper()}")
        print("   📝 说明: 特殊功能按键")


if __name__ == "__main__":
    print("\n🔍 开始检测额外按键功能...\n")
    
    if sys.platform != 'win32':
        print("⚠️  此脚本主要针对Windows系统")
    
    detect_key_function()
    
    print("\n💡 提示：将检测结果告诉我，我可以帮你确定最佳的按键命名")
