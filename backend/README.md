# GitHub Repository Onboarding Generator - Backend

A FastAPI-powered backend that generates personalized learning paths for GitHub repositories using AI.

## Features

- **GitHub API Integration**: Fetches repository data, structure, and metadata
- **AI-Powered Content Generation**: Uses Google's Gemini AI to create personalized learning paths
- **WebSocket Progress Tracking**: Real-time progress updates during generation
- **Fallback Mechanisms**: Graceful degradation when external services are unavailable
- **Multiple Interfaces**: Both web UI and REST API endpoints

## Architecture

### Core Components

1. **FastAPI Application** (`progress_tracker.py`)
   - Main application with CORS configuration
   - WebSocket support for real-time updates
   - Both HTML template and JSON API endpoints

2. **GitHub API Integration**
   - Repository metadata fetching
   - README content extraction
   - Language analysis
   - Directory structure traversal

3. **AI Integration**
   - Google Gemini AI for content generation
   - Structured prompts for consistent output
   - Fallback to template content when AI is unavailable

4. **Progress Tracking System**
   - WebSocket-based real-time updates
   - Connection management for multiple clients
   - Staged progress reporting (10%, 20%, 30%, etc.)

## API Endpoints

### Web Interface
- `GET /` - Main web interface for repository analysis
- `GET /generate` - Start generation process (with WebSocket updates)
- `GET /results/{client_id}` - Get generated results
- `WebSocket /ws/{client_id}` - Real-time progress updates

### REST API (for React frontend)
- `GET /api/learning-path` - Get sample learning path
- `POST /api/generate-learning-path` - Generate new learning path
- `GET /api/learning-path/{client_id}` - Get results by client ID

## Setup and Installation

### Prerequisites
- Python 3.8+
- GitHub Personal Access Token (optional, for higher rate limits)
- Google Gemini API Key (optional, for AI-generated content)

### Installation

1. **Clone and navigate to backend**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   ./run_progress_tracker.sh
   ```

## Environment Variables

Create a `.env` file with the following variables:

```env
# GitHub API Configuration (optional but recommended)
GITHUB_TOKEN=your_github_token_here

# Gemini AI Configuration (optional but recommended for AI features)
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=development
```

## Usage

### Web Interface
1. Navigate to `http://localhost:8000`
2. Enter a GitHub repository URL
3. Select experience level
4. Watch real-time progress updates
5. View generated learning path

### API Usage
```python
import requests

# Generate learning path
response = requests.post("http://localhost:8000/api/generate-learning-path", 
    json={
        "repo_url": "https://github.com/facebook/react",
        "experience_level": "intermediate",
        "focus_areas": []
    }
)

client_id = response.json()["client_id"]

# Poll for results
import time
while True:
    result = requests.get(f"http://localhost:8000/api/learning-path/{client_id}")
    if result.status_code == 200:
        learning_path = result.json()
        break
    time.sleep(2)
```

## Data Models

### Chapter
```python
class Chapter(BaseModel):
    id: int
    title: str
    description: str
    tasks: List[str]
    tips: List[str]
    next_steps: str
```

### LearningPath
```python
class LearningPath(BaseModel):
    overall_progress: int
    chapters: List[Chapter]
```

## Error Handling

The application includes comprehensive error handling:

- **GitHub API Failures**: Falls back to mock data
- **AI Generation Failures**: Uses template-based content
- **Network Issues**: Graceful degradation with informative messages
- **Rate Limiting**: Automatic retry mechanisms

## Performance Considerations

- **Async Operations**: All I/O operations are asynchronous
- **Connection Pooling**: Efficient WebSocket connection management
- **Caching**: Results are cached by client ID
- **Rate Limiting**: Respects GitHub API rate limits

## Development

### Project Structure
```
backend/
├── progress_tracker.py      # Main FastAPI application
├── github_learning_path_generator.py  # Alternative API-focused implementation
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variable template
├── templates/              # Jinja2 templates
├── static/                 # Static assets
└── run_*.sh               # Shell scripts for different run modes
```

### Running Different Modes

1. **Progress Tracker** (WebSocket + Web UI)
   ```bash
   ./run_progress_tracker.sh
   ```

2. **Full Stack** (Backend + Frontend)
   ```bash
   ./run_project.sh
   ```

3. **Development Mode**
   ```bash
   uvicorn progress_tracker:app --reload
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License.