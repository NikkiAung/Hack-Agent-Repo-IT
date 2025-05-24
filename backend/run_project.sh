#!/bin/bash

# Create necessary directories
mkdir -p templates
mkdir -p static
mkdir -p build

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Check if port is available
check_port() {
    if command -v lsof >/dev/null 2>&1; then
        lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
        return $?
    elif command -v nc >/dev/null 2>&1; then
        nc -z localhost $1 2>/dev/null
        return $?
    else
        # Fallback if neither lsof nor nc is available
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

# Get available port for backend
BACKEND_PORT=$(find_available_port 8000)

# Check if virtual environment exists, create one if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required packages for backend
pip install -r requirements.txt

# Go to project root for frontend
cd ..

# Install frontend dependencies if package.json exists
if [ -f "package.json" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Starting the full-stack application..."
echo "Backend will be available at http://localhost:$BACKEND_PORT"
echo "Frontend will be available at http://localhost:3000"
echo "Press Ctrl+C to stop both servers"

# Export backend port for frontend proxy
export REACT_APP_API_URL="http://localhost:$BACKEND_PORT"

# Run both servers with concurrently if available
if command -v npx &> /dev/null && [ -f "package.json" ]; then
    npx concurrently \
        "cd backend && uvicorn progress_tracker:app --reload --host 0.0.0.0 --port $BACKEND_PORT" \
        "npm start"
else
    echo "Warning: Starting backend only."
    echo "Please open another terminal and run 'npm start' in the project root to start the frontend."
    cd backend
    uvicorn progress_tracker:app --reload --host 0.0.0.0 --port $BACKEND_PORT
fi