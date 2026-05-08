@echo off
chcp 65001 >nul
title DouTracker - 开机自启管理

set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "LINK=%STARTUP_DIR%\DouTracker.lnk"
set "VBS_PATH=%APP_DIR%\launch_doutracker.vbs"

echo ============================================================
echo   DouTracker 开机自启管理
echo ============================================================
echo.

if exist "%LINK%" (
    echo [状态] 当前: 已启用开机自启
    echo.
    echo 操作:
    echo   [1] 禁用开机自启
    echo   [2] 重新创建自启快捷方式
    echo   [3] 退出
    echo.
    choice /c 123 /n /m "请选择 [1/2/3]: "
    if errorlevel 3 goto exit
    if errorlevel 2 goto recreate
    if errorlevel 1 goto disable
) else (
    echo [状态] 当前: 未启用开机自启
    echo.
    echo 操作:
    echo   [1] 启用开机自启
    echo   [2] 退出
    echo.
    choice /c 12 /n /m "请选择 [1/2]: "
    if errorlevel 2 goto exit
    if errorlevel 1 goto enable
)

:enable
echo.
echo 正在启用开机自启...
powershell -Command "$WScriptShell = New-Object -ComObject WScript.Shell; $Shortcut = $WScriptShell.CreateShortcut('%LINK%'); $Shortcut.TargetPath = 'wscript.exe'; $Shortcut.Arguments = '\"\"\"%VBS_PATH%\"\"\"'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.WindowStyle = 7; $Shortcut.IconLocation = '%APP_DIR%\assets\favicon.ico'; $Shortcut.Description = 'DouTracker 抖音博主数据面板'; $Shortcut.Save()"
echo [OK] 已添加到启动文件夹
echo       路径: %LINK%
echo       开机后将自动在后台启动 DouTracker
goto exit

:disable
echo.
echo 正在禁用开机自启...
del /q "%LINK%" 2>nul
echo [OK] 已从启动文件夹移除
goto exit

:recreate
del /q "%LINK%" 2>nul
goto enable

:exit
echo.
pause
