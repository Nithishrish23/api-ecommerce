#!/bin/bash

echo "========================================"
echo "Starting PCLMart Flask Backend Server"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python found!"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created!"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/Update dependencies
echo ""
echo "Installing/Updating dependencies..."
pip install -r requirements.txt

# Initialize database
echo ""
echo "Initializing database..."
python -c "from app.database import create; create()"

echo ""
echo "========================================"
echo "Starting Flask Server on http://localhost:5000"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Flask server
python main.py
