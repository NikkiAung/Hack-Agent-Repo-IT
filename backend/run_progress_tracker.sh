#!/bin/bash

# Create necessary directories
mkdir -p templates
mkdir -p static

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Set default port if not specified
PORT=${PORT:-8000}

# Check if port is available
check_port() {
    if command -v nc >/dev/null 2>&1; then
        nc -z localhost $1 2>/dev/null
        return $?
    else
        # Fallback if nc is not available
        python3 -c "import socket; s=socket.socket(); s.settimeout(1); result=s.connect_ex(('localhost',$1)); s.close(); exit(0 if result==0 else 1)" 2>/dev/null
        return $?
    fi
}

# Find available port
find_available_port() {
    local port=$1
    while check_port $port; do
        echo "Port $port is in use, trying $((port + 1))..."
        port=$((port + 1))
    done
    echo $port
}

# Get available port
AVAILABLE_PORT=$(find_available_port $PORT)

# Check if virtual environment exists, create one if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

echo "Starting Progress Tracker on port $AVAILABLE_PORT..."
echo "Access the web interface at: http://localhost:$AVAILABLE_PORT"
echo "API endpoints available at: http://localhost:$AVAILABLE_PORT/api/"
echo "Press Ctrl+C to stop the server"

# Start the application
uvicorn progress_tracker:app --host 0.0.0.0 --port $AVAILABLE_PORT --reload