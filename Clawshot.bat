@echo off
setlocal DisableDelayedExpansion
rem Run from the unpacked Clawshot folder, not from inside the zip.
if not exist "%~dp0uv.lock" (
    echo Unzip the whole Clawshot folder first, then double-click Clawshot.bat inside it.
    pause
    exit /b 1
)
if not exist "%~dp0scripts\start-windows.ps1" (
    echo Unzip the whole Clawshot folder first, then double-click Clawshot.bat inside it.
    pause
    exit /b 1
)
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-windows.ps1" %*
set "status=%errorlevel%"
if not "%status%"=="0" pause
exit /b %status%
