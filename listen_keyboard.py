"""
键盘按键监听脚本 - 用于捕获所有按键的原始扫描码和名称
用途：识别MK850键盘上未映射的多余按键
"""

import sys
import time

def try_keyboard_library():
    """尝试使用keyboard库监听（需要管理员权限）"""
    try:
        import keyboard
        
        print("=" * 60)
        print("键盘按键监听器")
        print("=" * 60)
        print("✅ 使用 keyboard 库监听")
        print("\n📌 说明：")
        print("   1. 请以【管理员权限】运行此脚本")
        print("   2. 按下你想测试的按键")
        print("   3. 查看输出的扫描码和按键名称")
        print("   4. 按 Ctrl+C 退出\n")
        print("-" * 60)
        
        pressed_keys = set()
        
        def on_key_event(event):
            key_info = {
                'name': event.name,
                'scan_code': event.scan_code,
                'event_type': event.event_type,
                'time': time.strftime('%H:%M:%S')
            }
            
            if event.event_type == 'down':
                pressed_keys.add(event.scan_code)
                print(f"[{key_info['time']}] ⬇️  按下 | "
                      f"扫描码: {key_info['scan_code']:3d} (0x{key_info['scan_code']:02X}) | "
                      f"按键: {key_info['name']:15s}")
            else:
                pressed_keys.discard(event.scan_code)
                print(f"[{key_info['time']}] ⬆️  抬起 | "
                      f"扫描码: {key_info['scan_code']:3d} (0x{key_info['scan_code']:02X}) | "
                      f"按键: {key_info['name']:15s}")
        
        # 注册监听器
        keyboard.hook(on_key_event)
        
        try:
            keyboard.wait()  # 保持程序运行
        except KeyboardInterrupt:
            print("\n" + "-" * 60)
            print(f"\n✅ 监听结束，共检测到 {len(pressed_keys)} 个不同的按键")
            if pressed_keys:
                print("\n检测到的扫描码列表：")
                for code in sorted(pressed_keys):
                    print(f"  扫描码 {code:3d} (0x{code:02X})")
            return True
            
    except ImportError:
        print("⚠️  keyboard 库未安装")
        print("   请运行: pip install keyboard")
        print("   或者使用方法2（Windows API）\n")
        return False
    except Exception as e:
        print(f"❌ keyboard 库监听失败: {e}")
        print("   可能需要管理员权限，尝试方法2...\n")
        return False


def try_windows_api():
    """使用Windows API低级钩子监听（无需额外库）"""
    try:
        import ctypes
        from ctypes import wintypes
        
        print("=" * 60)
        print("键盘按键监听器 - Windows API模式")
        print("=" * 60)
        print("✅ 使用 Windows API 低级钩子")
        print("\n📌 说明：")
        print("   1. 按下你想测试的按键")
        print("   2. 查看输出的扫描码")
        print("   3. 按 Ctrl+C 退出\n")
        print("-" * 60)
        
        # Windows API常量
        WH_KEYBOARD_LL = 13
        WM_KEYDOWN = 0x0100
        WM_KEYUP = 0x0101
        WM_SYSKEYDOWN = 0x0104
        WM_SYSKEYUP = 0x0105
        
        # 定义回调函数类型
        HOOKPROC = ctypes.WINFUNCTYPE(
            ctypes.c_int, 
            ctypes.c_int, 
            wintypes.WPARAM, 
            wintypes.LPARAM
        )
        
        detected_codes = set()
        
        def low_level_keyboard_handler(nCode, wParam, lParam):
            if nCode >= 0 and wParam in (WM_KEYDOWN, WM_KEYUP, WM_SYSKEYDOWN, WM_SYSKEYUP):
                # 从lParam提取扫描码
                scan_code = (lParam >> 16) & 0xFF
                is_extended = (lParam >> 24) & 0x01
                
                event_type = "按下" if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN) else "抬起"
                
                if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                    detected_codes.add(scan_code)
                
                ext_flag = "[扩展]" if is_extended else ""
                print(f"[{time.strftime('%H:%M:%S')}] {event_type:4s} | "
                      f"扫描码: {scan_code:3d} (0x{scan_code:02X}) {ext_flag}")
            
            # 调用下一个钩子
            return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)
        
        # 安装钩子
        hook = HOOKPROC(low_level_keyboard_handler)
        hook_id = ctypes.windll.user32.SetWindowsHookExA(
            WH_KEYBOARD_LL, 
            hook, 
            None, 
            0
        )
        
        if not hook_id:
            print("❌ 无法安装键盘钩子")
            return False
        
        print("✅ 钩子安装成功，开始监听...\n")
        
        try:
            msg = wintypes.MSG()
            while ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
        except KeyboardInterrupt:
            ctypes.windll.user32.UnhookWindowsHookEx(hook_id)
            print("\n" + "-" * 60)
            print(f"\n✅ 监听结束，共检测到 {len(detected_codes)} 个不同的扫描码")
            if detected_codes:
                print("\n检测到的扫描码列表：")
                for code in sorted(detected_codes):
                    print(f"  扫描码 {code:3d} (0x{code:02X})")
            return True
            
    except Exception as e:
        print(f"❌ Windows API监听失败: {e}")
        return False


if __name__ == "__main__":
    print("\n🔍 开始尝试监听键盘...\n")
    
    # 优先尝试keyboard库（更友好）
    if not try_keyboard_library():
        # 如果失败，尝试Windows API
        if sys.platform == 'win32':
            try_windows_api()
        else:
            print("❌ 当前系统不支持Windows API方法")
            print("   请安装 keyboard 库: pip install keyboard")
    
    print("\n💡 提示：将检测到的扫描码告诉我，我可以帮你添加到INI配置文件中")
