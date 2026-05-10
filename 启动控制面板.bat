@echo off
chcp 65001 >nul
title RGB灯光控制系统 - 虚拟键盘版
echo.
echo ============================================================
echo   🎨 RGB灯光同步控制系统 v2.2.0
echo   ✨ 状态: 生产就绪版 (Stable)
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
echo.
set /p choice="Enter choice (1-3): "

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
) else (
    echo.
    echo Invalid choice, exiting.
)

echo.
pause
