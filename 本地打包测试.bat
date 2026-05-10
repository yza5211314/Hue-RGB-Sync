@echo off
chcp 65001 >nul
title RGB灯光同步系统 - 本地打包脚本

echo ============================================================
echo   📦 开始本地打包测试 (PyInstaller)
echo ============================================================
echo.

:: 检查 PyInstaller
python -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未安装 PyInstaller，请运行: pip install pyinstaller
    pause
    exit /b
)

echo [1/2] 清理旧文件...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo [2/2] 正在执行打包...
python -m PyInstaller --onefile --windowed --name "Hue-RGB-Sync" ^
  --add-data "mk850_key_mapping.ini;." ^
  --add-data "devices;devices" ^
  --collect-all hidapi ^
  --collect-submodules devices ^
  --hidden-import devices.mk850_keyboard ^
  --hidden-import devices.tsg600_mouse ^
  --noupx ^
  --uac-admin ^
  gui_control.py

echo.
if %errorlevel% == 0 (
    echo ✅ 完成！文件位于 dist/Hue-RGB-Sync.exe
) else (
    echo ❌ 打包失败。
)
pause