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

# Install requirements
pip install -r requirements.txt

# Run the simplified GitHub app
echo "Starting the app on http://localhost:8000"
uvicorn simplified_github:app --reload