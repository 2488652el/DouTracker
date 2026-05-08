@echo off
chcp 65001 >nul
title DouTracker 安装器

echo.
echo =======================================================
echo   DouTracker - 抖音博主数据面板 安装向导
echo =======================================================
echo.

set "APP_DIR=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"

echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

echo [2/4] 安装依赖...
pip install -r "%APP_DIR%requirements.txt" -q
if errorlevel 1 (
    echo [警告] 部分依赖安装失败，请手动执行: pip install -r requirements.txt
)
echo.

echo [3/4] 生成启动脚本...
set "LAUNCHER=%APP_DIR%launch_doutracker.bat"
(
echo @echo off
echo cd /d "%APP_DIR%"
echo echo 启动 DouTracker...
echo start "" python "%APP_DIR%app.py"
echo timeout /t 3 /nobreak ^>nul
echo start "" http://127.0.0.1:8899
) > "%LAUNCHER%"
echo   已创建: launch_doutracker.bat

echo [4/4] 创建快捷方式...
powershell -Command ^
"$WScriptShell = New-Object -ComObject WScript.Shell; "^
"$Shortcut = $WScriptShell.CreateShortcut('%DESKTOP%\DouTracker.lnk'); "^
"$Shortcut.TargetPath = '%LAUNCHER%'; "^
"$Shortcut.WorkingDirectory = '%APP_DIR%'; "^
"$Shortcut.IconLocation = '%APP_DIR%assets\favicon.ico'; "^
"$Shortcut.Description = '抖音博主数据面板'; "^
"$Shortcut.Save()"

echo   已创建桌面快捷方式: DouTracker.lnk

echo.
echo =======================================================
echo   安装完成! 双击桌面的 DouTracker 图标即可启动。
echo =======================================================
echo.

pause
