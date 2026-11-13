@echo off
setlocal
rem Runtime starts ONLY the chosen game's bin\hookshot.exe or bin\longshot.exe with that
rem game's update check off, HOS_FS_OVERLAY cleared, HOS_MODS=<this pack> and --user <this pack>\user.
rem Missing mods support, extra mods or mismatched seed is a hard stop.
rem CLAWSHOT_DRY_RUN=1 verifies and prints the plan without starting the game.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" -Action play
set "RESULT=%ERRORLEVEL%"
pause
exit /b %RESULT%
