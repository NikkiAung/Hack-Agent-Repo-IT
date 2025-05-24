# agents.py
"""Hackathon‑ready CrewAI agent pack for the Agentic Code Navigator project.

This single module contains:
    • Minimal tool abstractions
    • Individual Agent definitions
    • Task templates
    • Assembly helper (get_crew) to wire everything together

You can copy‑paste this file into a blank repo, run `pip install crewai qdrant-client
gitpython tree_sitter_client openai neo4j` (or your preferred libs) and start
experimenting immediately.  All I/O‑heavy ops are stubbed so the agents are
safe to import even without external services; replace the TODOs with real
implementations during hacking.
"""
from __future__ import annotations

import os
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List

# === CrewAI core ===
from crewai import Agent, Task, Crew, LLM  # type: ignore  # crewai pydantic
from crewai.tools import BaseTool # type: ignore
from typing import Type, Optional, Dict, Any, List
from pydantic import BaseModel, Field


# Configure Anthropic Claude as the default LLM
anthropic_llm = LLM(
    model="anthropic/claude-sonnet-4-20250514",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# ---------------------------------------
# 1. Tool layer (skills shared by agents)
# ---------------------------------------


# === Base Tool Class ===

class BaseRepoTool(BaseTool):
    """Base class for repository analysis tools with common utilities."""
    
    def _validate_path(self, path: str) -> bool:
        """Validate if a path exists."""
        import os
        return os.path.exists(path)
    
    def _safe_execute(self, func, *args, **kwargs) -> str:
        """Execute function with error handling."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error in {self.__class__.__name__}: {str(e)}"
    
    def _log_operation(self, operation: str, details: str = "") -> None:
        """Log tool operations for debugging."""
        print(f"[{self.__class__.__name__}] {operation}: {details}")

# === Tool Classes ===

class GitCloneToolInput(BaseModel):
    """Input schema for GitCloneTool."""
    repo_url: str = Field(..., description="The URL of the git repository to clone")
    target_dir: str = Field(default="./repo", description="Directory where to clone the repository")

class GitCloneTool(BaseRepoTool):
    name: str = "git_clone_tool"
    description: str = "Clone a git repository to analyze its structure and content."
    args_schema: Type[BaseModel] = GitCloneToolInput
    
    def _run(self, repo_url: str, target_dir: str = "./repo") -> str:
        """Clone a git repository."""
        def clone_repo():
            import subprocess
            import os
            
            # Create target directory if it doesn't exist
            os.makedirs(target_dir, exist_ok=True)
            
            # Clone the repository
            result = subprocess.run(
                ["git", "clone", repo_url, target_dir],
                capture_output=True,
                text=True,
                check=True
            )
            
            self._log_operation("Clone", f"{repo_url} -> {target_dir}")
            return f"Successfully cloned repository to {target_dir}"
        
        return self._safe_execute(clone_repo)

class TreeSitterParseToolInput(BaseModel):
    """Input schema for TreeSitterParseTool."""
    file_path: str = Field(..., description="Path to the source code file to parse")
    language: str = Field(default="python", description="Programming language of the file")

class TreeSitterParseTool(BaseRepoTool):
    name: str = "tree_sitter_parse_tool"
    description: str = "Parse source code files using tree-sitter to extract AST information."
    args_schema: Type[BaseModel] = TreeSitterParseToolInput
    
    def _run(self, file_path: str, language: str = "python") -> str:
        """Parse source code file."""
        def parse_file():
            if not self._validate_path(file_path):
                return f"File not found: {file_path}"
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.split('\n')
            self._log_operation("Parse", f"{file_path} ({language})")
            return f"Parsed {file_path}: {len(lines)} lines, {len(content)} characters, language: {language}"
        
        return self._safe_execute(parse_file)

class EmbeddingToolInput(BaseModel):
    """Input schema for EmbeddingTool."""
    text: str = Field(..., description="Text content to embed")
    collection_name: str = Field(default="code_embeddings", description="Name of the Qdrant collection")

class EmbeddingTool(BaseRepoTool):
    name: str = "embed_qdrant_tool"
    description: str = "Generate embeddings for text and store in Qdrant vector database."
    args_schema: Type[BaseModel] = EmbeddingToolInput
    
    def _run(self, text: str, collection_name: str = "code_embeddings") -> str:
        """Generate embeddings for text."""
        def generate_embedding():
            import openai
            import os
            
            # Get OpenAI API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "Error: OPENAI_API_KEY environment variable not set"
                
            # Initialize OpenAI client
            client = openai.OpenAI(api_key=api_key)
            
            # Generate embedding
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            embedding = response.data[0].embedding
            self._log_operation("Embed", f"{len(text)} chars -> {len(embedding)} dims")
            return f"Generated embedding for text ({len(text)} chars) with {len(embedding)} dimensions"
        
        return self._safe_execute(generate_embedding)

class MermaidGenToolInput(BaseModel):
    """Input schema for MermaidGenTool."""
    description: str = Field(..., description="Description of the diagram to generate")
    diagram_type: str = Field(default="flowchart", description="Type of Mermaid diagram")

class MermaidGenTool(BaseRepoTool):
    name: str = "mermaid_gen_tool"
    description: str = "Generate Mermaid diagram syntax from description."
    args_schema: Type[BaseModel] = MermaidGenToolInput
    
    def _run(self, description: str, diagram_type: str = "flowchart") -> str:
        """Generate Mermaid diagram."""
        def generate_diagram():
            # Basic Mermaid diagram generation based on type
            if diagram_type == "flowchart":
                mermaid_code = f"""flowchart TD
    A[Start] --> B[{description}]
    B --> C[End]"""
            elif diagram_type == "sequence":
                mermaid_code = f"""sequenceDiagram
    participant A as User
    participant B as System
    A->>B: {description}
    B-->>A: Response"""
            else:
                mermaid_code = f"""graph TD
    A[{description}]"""
                
            self._log_operation("Generate", f"{diagram_type} diagram")
            return f"Generated Mermaid {diagram_type} diagram:\n{mermaid_code}"
        
        return self._safe_execute(generate_diagram)

class GitAnalyticsToolInput(BaseModel):
    """Input schema for GitAnalyticsTool."""
    repo_path: str = Field(default="./repo", description="Path to the git repository")
    file_pattern: str = Field(default="*.py", description="File pattern to analyze")

class GitAnalyticsTool(BaseRepoTool):
    name: str = "git_heatmap_tool"
    description: str = "Analyze git commit history to generate a heatmap of code changes."
    args_schema: Type[BaseModel] = GitAnalyticsToolInput
    
    def _run(self, repo_path: str = "./repo", file_pattern: str = "*.py") -> str:
        """Analyze git commit history."""
        def analyze_git_history():
            import subprocess
            
            if not self._validate_path(repo_path):
                return f"Repository path not found: {repo_path}"
                
            # Get git log with file statistics
            result = subprocess.run(
                ["git", "log", "--stat", "--oneline", "--", file_pattern],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = result.stdout.split('\n')
            commit_count = len([line for line in lines if line.strip() and not line.startswith(' ')])
            
            self._log_operation("Analyze", f"{commit_count} commits for {file_pattern}")
            return f"Git heatmap analysis for {file_pattern} in {repo_path}: {commit_count} commits analyzed"
        
        return self._safe_execute(analyze_git_history)


# ---------------------------------------
# 2. Agent definitions
# ---------------------------------------


# Tool instances for agents
git_clone_tool = GitCloneTool()
tree_sitter_parse_tool = TreeSitterParseTool()
embed_qdrant_tool = EmbeddingTool()
mermaid_gen_tool = MermaidGenTool()
git_heatmap_tool = GitAnalyticsTool()


RepoIngestor = Agent(
    role="Repository Analysis Specialist",
    goal="Clone and structurally parse GitHub repositories into an AST graph for downstream analysis.",
    backstory="You are an expert at analyzing code repositories. You can quickly clone repos and parse their structure to understand the codebase architecture.",
    tools=[git_clone_tool, tree_sitter_parse_tool],
    llm=anthropic_llm,
)

DependencyResolver = Agent(
    role="Security and Dependency Analyst",
    goal="Detect package managers, build a software bill‑of‑materials and flag known CVEs using OSV.",
    backstory="You specialize in software supply chain security, identifying dependencies and potential vulnerabilities in codebases.",
    tools=[],  # add SBOM tool later
    llm=anthropic_llm,
)

EmbedIndexer = Agent(
    role="Semantic Search Engineer",
    goal="Embed code & docs into Qdrant for semantic search.",
    backstory="You excel at creating semantic representations of code and documentation to enable intelligent search and retrieval.",
    tools=[embed_qdrant_tool],
    llm=anthropic_llm,
)

BriefIntroSynthesizer = Agent(
    role="Technical Documentation Writer",
    goal="Write a concise README summary (what, tech, arch).",
    backstory="You are skilled at distilling complex technical information into clear, concise documentation that helps developers quickly understand projects.",
    tools=[],
    llm=anthropic_llm,
)

ComponentMapper = Agent(
    role="Software Architecture Visualizer",
    goal="Produce interactive Mermaid mind‑maps of repo structure.",
    backstory="You specialize in creating visual representations of software architecture, making complex systems easy to understand through diagrams.",
    tools=[mermaid_gen_tool],
    llm=anthropic_llm,
)

HeatmapAnalyst = Agent(
    role="Code Evolution Analyst",
    goal="Analyse git history to find hotspots and unstable files.",
    backstory="You are an expert at analyzing code change patterns and identifying areas of high churn that may indicate technical debt or instability.",
    tools=[git_heatmap_tool],
    llm=anthropic_llm,
)

TaskContextFinder = Agent(
    role="Code Context Retrieval Specialist",
    goal="Given a natural language task, retrieve and rank relevant code parts.",
    backstory="You excel at understanding natural language queries and mapping them to relevant code sections using semantic search.",
    tools=[],  # uses Qdrant search via built‑in CrewAI search
    llm=anthropic_llm,
)

PRReviewer = Agent(
    role="Senior Code Reviewer",
    goal="Review pull‑requests for style, bugs and security issues.",
    backstory="You are an experienced code reviewer with a keen eye for bugs, security vulnerabilities, and code quality issues.",
    tools=[],
    llm=anthropic_llm,
)

DiagramBot = Agent(
    role="UML Diagram Generator",
    goal="Generate UML diagrams from code or diffs on request.",
    backstory="You specialize in creating clear UML diagrams that help visualize code structure, relationships, and changes.",
    tools=[mermaid_gen_tool],
    llm=anthropic_llm,
)

TutorBot = Agent(
    role="Code Mentor and Educator",
    goal="Answer newcomers' questions about any file or function in the repo.",
    backstory="You are a patient and knowledgeable mentor who excels at explaining complex code concepts in simple terms for newcomers.",
    tools=[],
    llm=anthropic_llm,
)

WorkflowPlanner = Agent(
    role="Project Manager and Task Orchestrator",
    goal="Break high‑level user goals into ordered agent tasks and monitor execution.",
    backstory="You are an experienced project manager who excels at breaking down complex goals into manageable tasks and coordinating team efforts.",
    tools=[],
    llm=anthropic_llm,
)

# ----------------------------------------------------
# 3. Task templates that the Planner can instantiate
# ----------------------------------------------------

tasks_catalog = {
    "ingest": lambda repo_url: Task(
        description=f"Clone and parse {{repo_url}} into AST JSON.",
        expected_output="path of ast.json",
        agent=RepoIngestor,
        async_execution=True,
        output_file="ast.json",
    ),
    "embed": lambda ast_path: Task(
        description="Embed extracted code/documentation chunks into vector store.",
        expected_output="confirmation of embeddings stored in vector database",
        agent=EmbedIndexer,
        async_execution=True,
        context={"ast_path": ast_path},
    ),
    "brief_intro": lambda repo_meta: Task(
        description="Generate README bullets: what, tech, architecture.",
        expected_output="markdown formatted brief introduction with key points",
        agent=BriefIntroSynthesizer,
        context=repo_meta,
    ),
    "map_components": lambda ast_path: Task(
        description="Build Mermaid mind‑map of modules/classes/functions.",
        expected_output="mermaid diagram code representing the component structure",
        agent=ComponentMapper,
        context={"ast": ast_path},
    ),
    "heatmap": lambda repo_path: Task(
        description="Produce JSON heatmap of commit counts per file.",
        expected_output="JSON object with file paths as keys and commit counts as values",
        agent=HeatmapAnalyst,
        context={"repo_path": repo_path},
    ),
}


# ----------------------------------------
# 4. Crew assembly helper for applications
# ----------------------------------------

def get_crew() -> Crew:
    """Return a Crew wired with all available Agents.

    Apps can import this and call `crew.kickoff(inputs=…)`.
    """

    agents = [
        RepoIngestor,
        DependencyResolver,
        EmbedIndexer,
        BriefIntroSynthesizer,
        ComponentMapper,
        HeatmapAnalyst,
        TaskContextFinder,
        PRReviewer,
        DiagramBot,
        TutorBot,
        WorkflowPlanner,
    ]

    # Dummy bootstrap task – real planners will enqueue their own.
    bootstrap = Task(
        description="Idle bootstrap – real execution starts via Planner agent.",
        expected_output="workflow plan for repository analysis",
        agent=WorkflowPlanner,
    )

    return Crew(
        agents=agents,
        tasks=[bootstrap],
        global_namespace={"tasks_catalog": tasks_catalog},
    )


# --- Entry‑point for local testing ---
if __name__ == "__main__":
    crew = get_crew()
    result = crew.kickoff(inputs={"repo_url": "https://github.com/tiangolo/fastapi"})
    print("\n\n=== DEMO RESULT ===\n", result)
