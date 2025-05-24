# Repository Analysis Platform

An intelligent repository analysis platform powered by CrewAI agents, providing automated code analysis, architecture insights, and conversational assistance for software development teams.

## 🚀 Features

- **Automatic Repository Ingestion**: Clone and analyze any GitHub repository
- **AI-Powered Code Analysis**: Multi-agent system for comprehensive code understanding
- **Architecture Visualization**: Generate architecture diagrams and documentation
- **Conversational Assistant**: Chat with your repository using RAG-based AI
- **Memory Layer**: Persistent knowledge storage with Neo4j and vector databases
- **Modern Web Interface**: Next.js frontend with beautiful UI components

## 🏗️ Architecture

### Backend (Python)
- **FastAPI**: RESTful API server
- **CrewAI**: Multi-agent orchestration framework
- **LangChain**: LLM integration and tooling
- **Vector Databases**: Weaviate/Qdrant for embeddings
- **Graph Database**: Neo4j for relationship mapping
- **PostgreSQL**: Structured data storage

### Frontend (Next.js)
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Radix UI**: Accessible component library
- **NextAuth.js**: Authentication system

### AI Agents
1. **Repo Analyzer Agent**: Repository structure and metadata analysis
2. **Code Insight Agent**: Deep code analysis and pattern detection
3. **Architecture Agent**: System design and architecture documentation
4. **Documentation Generator**: Automated documentation creation
5. **Development Mentor**: Code review and improvement suggestions
6. **Task Suggester**: Development task recommendations
7. **Memory Agent**: Knowledge persistence and retrieval

## 🛠️ Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (optional, for databases)
- Git

### Environment Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Configure your API keys and database connections in `.env`:

```bash
# Required: At least one LLM API key
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Vector Database (choose one)
WEAVIATE_URL=http://localhost:8080
QDRANT_URL=http://localhost:6333

# Graph Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=repo_analysis
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

### Backend Setup

1. Install Python dependencies:
```bash
pip install -e .
```

2. Start the FastAPI server:
```bash
python server.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install Node.js dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📖 Usage

### Analyzing a Repository

1. **Via Web Interface:**
   - Open `http://localhost:3000`
   - Enter a GitHub repository URL
   - Click "Analyze Repository"
   - Wait for the analysis to complete

2. **Via API:**
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo"}'
```

### Chatting with Repository

1. **Via Web Interface:**
   - Navigate to an analyzed repository
   - Use the chat interface to ask questions

2. **Via API:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_id": "repo_id_here",
    "message": "How does the authentication system work?"
  }'
```

## 🔧 Development

### Project Structure

```
├── backend/
│   ├── agents/          # CrewAI agents and tools
│   ├── api/             # FastAPI routes and models
│   ├── services/        # Business logic services
│   └── config.py        # Configuration management
├── app/                 # Next.js frontend
├── components/          # React components
├── lib/                 # Utility libraries
├── server.py           # FastAPI server entry point
├── main.py             # CrewAI crew entry point
└── pyproject.toml      # Python dependencies
```

### Adding New Agents

1. Create a new agent class in `backend/agents/`
2. Define the agent's role, goal, and backstory
3. Assign relevant tools to the agent
4. Add the agent to the crew in `get_crew()` function

### Adding New Tools

1. Create a tool class inheriting from `BaseTool`
2. Implement the `_run()` method
3. Add proper error handling and logging
4. Register the tool with relevant agents

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details
