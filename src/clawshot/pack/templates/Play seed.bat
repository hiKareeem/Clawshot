@echo off
setlocal
rem Based on the approved chest-ocarina-storms new-game launcher.
rem Runtime starts ONLY bin\hookshot.exe with HOOKSHOT_NO_UPDATE_CHECK=1,
rem HOS_FS_OVERLAY=<this pack>\seed\romfs and --user <this pack>\user.
rem Missing bin exe or mismatched seed is a hard stop; no root-launcher fallback.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" -Action play
set "RESULT=%ERRORLEVEL%"
pause
exit /b %RESULT%
