@echo off
setlocal
rem Runtime starts ONLY bin\hookshot.exe with HOOKSHOT_NO_UPDATE_CHECK=1,
rem HOS_FS_OVERLAY cleared, HOS_MODS=<this pack> and --user <this pack>\user.
rem Missing mods support, extra mods or mismatched seed is a hard stop.
rem CLAWSHOT_DRY_RUN=1 verifies and prints the plan without starting the game.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" -Action play
set "RESULT=%ERRORLEVEL%"
pause
exit /b %RESULT%
