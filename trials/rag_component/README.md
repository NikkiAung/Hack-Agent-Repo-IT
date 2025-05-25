# GitHub Repository RAG Component

A modular component for analyzing and querying GitHub repositories using Retrieval Augmented Generation (RAG) with Gemini 2.0 Flash embeddings.

## Features

- **Repository Analysis**: Analyze GitHub repositories for structure, code patterns, and architecture
- **Semantic Querying**: Ask natural language questions about repositories
- **Mock Mode**: Fallback to mock responses when dependencies are unavailable or rate limits are hit
- **Caching**: Automatic response caching to avoid repeated API calls
- **Graceful Degradation**: Works even with partial dependency availability

## Installation

### Prerequisites

- Python 3.8+
- Google API key for Gemini (set as `GOOGLE_API_KEY` environment variable)
- GitHub API token (optional, but recommended to avoid rate limits)

### Dependencies

This component has the following optional dependencies:

- `crewai` and `crewai-tools`: For agent-based analysis
- `embedchain`: For RAG functionality
- `PyGithub`: For GitHub API access
- `google-generativeai`: For Gemini embeddings and LLM

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/vishnutejaa/Hack-Agent-Repo-IT.git
   cd Hack-Agent-Repo-IT
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   ```bash
   export GOOGLE_API_KEY="your-google-api-key"
   export GITHUB_TOKEN="your-github-token"  # Optional but recommended
   ```

## Usage

### Basic Usage

```python
from trials.rag_component import GithubRepoAnalysisAgents

# Initialize the agents
agents = GithubRepoAnalysisAgents(llm="google")

# Define a repository URL
repo_url = "https://github.com/username/repository"

# Query information about the repository
query = "What is the purpose of this repository?"
answer = agents.query_repository(repo_url, query)
print(answer)

# Analyze the repository
analysis = agents.analyze_repository(repo_url)
print(analysis)
```

### Using the RAG Tool Directly

```python
from trials.rag_component import GithubRepoRagTool

# Initialize the RAG tool
rag_tool = GithubRepoRagTool()

# Add a repository
repo_url = "https://github.com/username/repository"
rag_tool.add_github_repo(repo_url)

# Query the knowledge base
query = "How is the code structured?"
answer = rag_tool.run(query)
print(answer)
```

### Using the CLI Interface

The component includes a command-line interface for easy usage:

```bash
# Run a query
python -m trials.rag_component.cli --repo https://github.com/username/repository --query "What is the purpose of this repository?"

# Run a full analysis
python -m trials.rag_component.cli --repo https://github.com/username/repository --analyze

# Check available dependencies
python -m trials.rag_component.cli --check-deps
```

### Demo Script

For an interactive experience, try the demo script:

```bash
# Interactive demo
python trials/demo_rag_agents.py

# Single query demo
python trials/demo_rag_agents.py --query "What is the purpose of this repository?"

# Use a specific repository
python trials/demo_rag_agents.py --repo https://github.com/username/repository

# Force mock mode for testing
python trials/demo_rag_agents.py --mock
```

## Configuration

You can customize the RAG component with a configuration dictionary:

```python
config = {
    "llm": {
        "provider": "google",
        "config": {
            "model": "gemini-2.0-flash",
            "temperature": 0.1,
        }
    },
    "embedder": {
        "provider": "google",
        "config": {
            "model": "text-embedding-004",
        }
    },
    "chunker": {
        "chunk_size": 2000,
        "chunk_overlap": 300,
    }
}

agents = GithubRepoAnalysisAgents(llm="google", config=config)
```

## Architecture

The component is structured as follows:

- `trials/rag_component/`: Main package directory
  - `__init__.py`: Package exports
  - `cli.py`: Command-line interface
  - `agents/`: Agent implementations
    - `github_repo_analysis_agents.py`: GitHub repository analysis agents
  - `tools/`: Tool implementations
    - `github_repo_rag_tool.py`: GitHub repository RAG tool
  - `utils/`: Utility modules
    - `dependencies.py`: Dependency management
    - `mock_responses.py`: Mock response generation

## License

MIT

## Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) for the agent framework
- [EmbedChain](https://github.com/embedchain/embedchain) for RAG implementation
- [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API access
- [Google Generative AI](https://github.com/google/generative-ai-python) for Gemini models 