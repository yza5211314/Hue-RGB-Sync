import os
import shutil
import glob

def cleanup():
    """清理项目中的无用文件和目录"""
    print("🧹 开始清理项目文件...")
    
    # 1. 需要删除的特定文件 (旧的测试脚本和日志)
    files_to_remove = [
        'main.py', 
        'verify_mapping.py', 
        'diagnose.py', 
        'obvious_test.py', 
        'check_admin.py',
        'test_keyboard_direct.py',
        'key_mapping_quick_ref.py'
    ]
    
    # 2. 需要删除的目录
    dirs_to_remove = [
        '__pycache__',
        'build',
        'dist',
        '.pytest_cache',
        '.venv',
        'venv'
    ]
    
    # 执行文件删除
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"  已删除文件: {file}")
            except Exception as e:
                print(f"  无法删除文件 {file}: {e}")

    # 执行目录删除
    for folder in dirs_to_remove:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"  已递归删除目录: {folder}")
            except Exception as e:
                print(f"  无法删除目录 {folder}: {e}")

    # 清理通配符文件 (如 .log 文件)
    for log_file in glob.glob("*.log"):
        os.remove(log_file)
        print(f"  已清理日志: {log_file}")

    print("✨ 清理完成！现在你的目录非常整洁，可以放心上传到 GitHub 了。")

if __name__ == "__main__":
    cleanup()