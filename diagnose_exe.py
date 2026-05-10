"""
EXE 打包后诊断工具
用于检查打包后的程序是否能正常运行
"""
import sys
import os

def diagnose():
    """诊断打包环境"""
    print("=" * 60)
    print("Hue RGB Sync - 打包诊断工具")
    print("=" * 60)
    
    # 检查是否是打包后的EXE
    is_frozen = getattr(sys, 'frozen', False)
    print(f"\n✓ 打包状态: {'已打包(EXE)' if is_frozen else '开发模式(Python)'}")
    
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        print(f"✓ 内部临时路径 (_MEIPASS): {meipass}")

    if is_frozen:
        print(f"✓ 可执行文件路径: {sys.executable}")
        base_dirs = [os.path.dirname(sys.executable)]
        if meipass:
            base_dirs.append(meipass)
    else:
        base_dirs = [os.path.dirname(__file__)]
    
    print(f"✓ 检查路径列表: {base_dirs}")
    
    # 检查配置文件
    print(f"\n配置文件检查:")
    for bp in base_dirs:
        ini_path = os.path.join(bp, 'mk850_key_mapping.ini')
        exists = os.path.exists(ini_path)
        print(f"  路径: {ini_path}")
        print(f"  存在: {'✓ 是' if exists else '✗ 否'}")
        if exists:
            print(f"  大小: {os.path.getsize(ini_path)} 字节")
    
    # 检查设备模块
    print(f"\n设备模块检查:")
    for bp in base_dirs:
        devices_path = os.path.join(bp, 'devices')
        exists = os.path.exists(devices_path)
        print(f"  路径: {devices_path}")
        print(f"  存在: {'✓ 是' if exists else '✗ 否'}")
        if exists:
            files = os.listdir(devices_path)
            print(f"  文件列表: {', '.join(files)}")
    
    # 检查 hidapi
    try:
        import hidapi
        print(f"\n✓ hidapi 模块: 已安装")
    except ImportError as e:
        print(f"\n✗ hidapi 模块: 缺失 - {e}")
    
    # 检查 Pillow
    try:
        from PIL import Image
        print(f"✓ Pillow 模块: 已安装")
    except ImportError as e:
        print(f"✗ Pillow 模块: 缺失 - {e}")
    
    print("\n" + "=" * 60)
    print("诊断完成!")
    print("=" * 60)
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    diagnose()
