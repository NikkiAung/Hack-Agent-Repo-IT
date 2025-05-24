#!/bin/bash

# Create necessary directories
mkdir -p templates
mkdir -p static

# Check if virtual environment exists, create one if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install fastapi uvicorn jinja2 python-multipart

# Run the simple form app
echo "Starting the simple form app on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
uvicorn simple_form:app --reload