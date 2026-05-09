@echo off
chcp 65001 >nul
title RGB灯光控制系统 - 虚拟键盘版
echo.
echo ============================================================
echo   🎨 RGB灯光同步控制系统 v2.0.3
echo   ✨ 新增: 虚拟键盘控制面板
echo ============================================================
echo.
echo 正在启动图形界面...
echo.
echo 💡 新功能提示:
echo   • 完整的MK850键盘可视化
echo   • 点击虚拟按键即可点亮实体键盘
echo   • 实时颜色预览和同步
echo   • 支持RGB滑块、预设按钮、屏幕取色
echo.
echo ============================================================
echo.

python gui_control.py

if errorlevel 1 (
    echo.
    echo ❌ 启动失败，请检查:
    echo   1. Python是否正确安装
    echo   2. 依赖包是否安装 (pip install hidapi Pillow)
    echo   3. 设备是否正确连接
    echo.
    pause
)

:: 检查是否以管理员权限运行
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run
) else (
    echo.
    echo ========================================
    echo   Need Administrator Permission
    echo ========================================
    echo.
    echo This program needs admin rights to control
    echo HID devices (RGB keyboard and mouse).
    echo.
    echo Requesting administrator permission...
    echo.
    timeout /t 2 >nul
    
    :: Use PowerShell to request admin rights
    PowerShell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:run
cls
echo.
echo ========================================
echo   RGB Lighting Sync System
echo   Running as Administrator
echo ========================================
echo.
echo Current User: %USERNAME%
echo Working Dir: %CD%
echo.
echo Please select mode:
echo.
echo [1] GUI Mode (Recommended)
echo [2] Command Line Mode
echo [3] Test Device Connection
echo [4] Keyboard Debug Test (with sound)
echo [5] Full Diagnostic
echo [6] Check Admin Permission
echo.
set /p choice="Enter choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Starting GUI...
    python gui_control.py
) else if "%choice%"=="2" (
    echo.
    echo Starting CLI mode...
    python main.py
) else if "%choice%"=="3" (
    echo.
    echo Testing device connection...
    python -c "from rgb_sync_controller import RGBSyncController; c = RGBSyncController(); c.auto_scan_devices()"
) else if "%choice%"=="4" (
    echo.
    echo Starting keyboard debug test...
    python obvious_test.py
) else if "%choice%"=="5" (
    echo.
    echo Starting full diagnostic...
    python diagnose.py
) else if "%choice%"=="6" (
    echo.
    echo Checking admin permission...
    python check_admin.py
) else (
    echo.
    echo Invalid choice, exiting.
)

echo.
pause
