@echo off
setlocal
rem Version preflight runs before uv; never starts the game.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" -Action make
set "RESULT=%ERRORLEVEL%"
pause
exit /b %RESULT%
