# GitHub Repository RAG Agents

This module provides specialized agents for analyzing GitHub repositories using Retrieval Augmented Generation (RAG) with Google's Gemini 2.0 Flash model.

## Features

- 🤖 **Specialized AI Agents**: Different agents for repository structure analysis, code insight, architecture understanding, and documentation generation
- 🔍 **Comprehensive Analysis**: Analyze repository structure, code patterns, architecture, and data flow
- 📚 **Documentation Generation**: Create comprehensive documentation based on repository analysis
- 💬 **Question Answering**: Ask specific questions about the repository and get informed answers
- 🌐 **GitHub Integration**: Automatically analyze any public GitHub repository
- 🧠 **Gemini 2.0 Flash**: Powered by Google's state-of-the-art Gemini 2.0 Flash model for embeddings and reasoning

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-directory>/trials
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

Alternatively, install the dependencies manually:

```bash
pip install crewai crewai-tools embedchain PyGithub python-dotenv google-generativeai
```

## Configuration

Create a `.env` file in the `trials` directory with your API keys:

```
# Google API key for Gemini 2.0 Flash
GOOGLE_API_KEY=your-google-api-key

# GitHub API token (optional, for higher rate limits)
GITHUB_TOKEN=your-github-token
```

## Usage

### Demo Script

The easiest way to use the RAG agents is through the demo script:

```bash
# Full repository analysis
python demo_rag_agents.py --repo https://github.com/username/repository --analyze

# Query specific information
python demo_rag_agents.py --repo https://github.com/username/repository --query "What is the main architecture of this application?"
```

Options:
- `--repo`: GitHub repository URL (required)
- `--analyze`: Run a full repository analysis
- `--query`: Ask a specific question about the repository
- `--gemini-key`: Google Gemini API key (if not in .env)
- `--github-token`: GitHub API token (if not in .env)

### Python API

You can also use the RAG agents directly in your Python code:

```python
import os
from rag_agents import GithubRepoAnalysisAgents

# Set Google API key
os.environ["GOOGLE_API_KEY"] = "your-google-api-key"

# Initialize agents
repo_agents = GithubRepoAnalysisAgents(llm="google")

# Analyze a repository
repo_url = "https://github.com/username/repository"
analysis = repo_agents.analyze_repository(repo_url)
print(analysis)

# Query specific information
answer = repo_agents.query_repository(
    repo_url, 
    "What is the main purpose of this repository and how is it structured?"
)
print(answer)
```

## Custom RAG Tool

You can also use the `GithubRepoRagTool` directly for more advanced use cases:

```python
from rag_agents import GithubRepoRagTool

# Initialize the RAG tool
rag_tool = GithubRepoRagTool(
    name="my_github_knowledge",
    description="Answer questions about GitHub repositories",
    summarize=True,  # Enable summarization of retrieved content
    config={
        # Optional custom configuration
        "llm": {
            "provider": "google",
            "config": {
                "model": "gemini-2.0-flash",
                "temperature": 0.1,  # Lower temperature for more focused responses
            }
        },
        "chunker": {
            "chunk_size": 2000,  # Larger chunks for more context
            "chunk_overlap": 300,
        }
    }
)

# Add a GitHub repository
rag_tool.add_github_repo(
    repo_url="https://github.com/username/repository",
    max_files=100,  # Process more files
    file_extensions=['.py', '.md', '.js']  # Focus on specific file types
)

# Query the knowledge base
answer = rag_tool.run("How is error handling implemented in this repository?")
print(answer)
```

## Agent Types

The module includes several specialized agents:

1. **Repository Structure Analyzer**: Analyzes the structure and organization of the repository
2. **Code Insight Specialist**: Understands and summarizes code functionality
3. **Architecture Designer**: Analyzes system architecture and component interactions
4. **Documentation Generator**: Creates comprehensive documentation
5. **Repository Guide**: Answers questions and guides new developers

## Customization

You can customize the RAG tool configuration to use different models or embedding providers:

```python
custom_config = {
    "llm": {
        "provider": "google",  # or "openai", "anthropic", etc.
        "config": {
            "model": "gemini-2.0-flash",  # or any other supported model
            "temperature": 0.2,
        }
    },
    "embedder": {
        "provider": "google",
        "config": {
            "model": "text-embedding-004",
            "vector_dimension": 768,
        }
    },
    "vectordb": {
        "provider": "chroma",  # or "weaviate", "pinecone", etc.
        "config": {
            "collection_name": "github_repos",
            "persist_directory": "./chroma_db"
        }
    }
}

# Initialize with custom config
rag_tool = GithubRepoRagTool(config=custom_config)
```

## Limitations

- The tool is limited by GitHub API rate limits (higher with a GitHub token)
- Very large repositories may be processed partially (default max: 50 files)
- Some binary files or complex code may not be properly analyzed
- The quality of analysis depends on the quality of the repository's code and documentation

## License

[MIT License](LICENSE) 