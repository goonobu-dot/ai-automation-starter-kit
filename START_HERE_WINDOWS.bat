@echo off
setlocal
cd /d "%~dp0"

echo Preparing a safe business automation example.
echo No API key or client data is required.
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 scripts\first_start.py --open --language en
) else (
  where python >nul 2>nul
  if not %errorlevel%==0 (
    echo Python 3 was not found. Ask Codex to help install Python 3, then double-click this file again.
    pause
    exit /b 1
  )
  python scripts\first_start.py --open --language en
)

if not %errorlevel%==0 (
  echo Setup did not finish. Show the error above to Codex.
  pause
  exit /b 1
)

echo.
echo Ready. Continue from "Do only this next" in the browser.
pause
