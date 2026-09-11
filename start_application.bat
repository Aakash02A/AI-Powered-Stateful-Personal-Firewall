@echo off
setlocal

set "ROOT=%~dp0"
set "PYTHON=python"

if exist "%ROOT%venv\Scripts\python.exe" set "PYTHON=%ROOT%venv\Scripts\python.exe"
if exist "%ROOT%.venv\Scripts\python.exe" set "PYTHON=%ROOT%.venv\Scripts\python.exe"

if not exist "%ROOT%backend\firewall\cli.py" (
    echo Could not find the backend at "%ROOT%backend".
    pause
    exit /b 1
)

if not exist "%ROOT%frontend\index.html" (
    echo Could not find the dashboard at "%ROOT%frontend".
    pause
    exit /b 1
)

echo Starting the Personal Firewall API...
start "Firewall API" /D "%ROOT%backend" cmd /k ""%PYTHON%" -m firewall.cli start-api"

echo Starting the Personal Firewall dashboard...
start "Firewall Dashboard" /D "%ROOT%frontend" cmd /k ""%PYTHON%" -m http.server 5173"

timeout /t 2 /nobreak >nul
start "" "http://localhost:5173/index.html"

endlocal
