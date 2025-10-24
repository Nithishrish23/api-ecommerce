@echo off
echo ========================================
echo Starting PCLMart Flask Backend Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/Update dependencies
echo.
echo Installing/Updating dependencies...
pip install -r requirements.txt

REM Initialize database
echo.
echo Initializing database...
python -c "from app.database import create; create()"

echo.
echo ========================================
echo Starting Flask Server on http://localhost:5000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start Flask server
python main.py

pause
