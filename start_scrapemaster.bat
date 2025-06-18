@echo off
setlocal enabledelayedexpansion

echo.
echo ???? ScrapeMaster Intelligence Platform
echo =====================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo ??? Virtual environment not found. Run deploy.ps1 first.
    pause & exit /b 1
)

if not exist "src\app.py" (
    echo ??? Application not found. Check installation.
    pause & exit /b 1
)

call venv\Scripts\activate.bat
if !errorlevel! neq 0 (
    echo ??? Virtual environment activation failed
    pause & exit /b 1
)

if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo ???? Starting ScrapeMaster Intelligence...
echo ???? Dashboard: http://localhost:8501
echo ???? Revenue Target: $15,000 MRR by Month 3
echo.

streamlit run src\app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false

if !errorlevel! neq 0 (
    echo ??? Application startup failed
    pause & exit /b 1
)
