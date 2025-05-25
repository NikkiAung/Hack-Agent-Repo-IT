#!/usr/bin/env python3
"""
RAG Agents for GitHub Repository Analysis

This module implements specialized agents for repository analysis using
Retrieval Augmented Generation (RAG) with Gemini 2.5 Flash embeddings.
"""

import os
import logging
import hashlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import crewai
import crewai_tools
from crewai.tools import tool

# Import the GithubRepoRagTool from the dedicated module
from trials.rag_component.tools.github_repo_rag_tool import GithubRepoRagTool

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CrewAI imports
try:
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import RagTool
    import crewai_tools
    HAS_CREWAI = True
except ImportError:
    logger.warning("CrewAI not installed. Run: pip install crewai crewai-tools")
    HAS_CREWAI = False
    # Define placeholders
    class Agent: pass
    class Task: pass
    class Crew: pass
    class Process: pass
    class RagTool: pass
    def tool(func): return func

# Embedchain for RAG implementation
try:
    from embedchain import App as EmbedchainApp
    HAS_EMBEDCHAIN = True
except ImportError:
    logger.warning("Embedchain not installed. Run: pip install embedchain")
    HAS_EMBEDCHAIN = False

# GitHub API client
try:
    from github import Github
    from github.Repository import Repository
    HAS_GITHUB = True
except ImportError:
    logger.warning("PyGithub not installed. Run: pip install PyGithub")
    HAS_GITHUB = False
    # Define a placeholder for the Repository type hint
    class Repository:
        """Placeholder for the GitHub Repository class when PyGithub is not installed."""
        def __init__(self, *args, **kwargs):
            self.name = "placeholder"
            self.owner = type('obj', (object,), {'login': 'placeholder'})
            self.description = "PyGithub not installed"
            self.updated_at = None
            self.stargazers_count = 0
            self.forks_count = 0
            self.language = None
        
        def get_contents(self, path):
            """Placeholder for get_contents method."""
            return []
            
        def get_topics(self):
            """Placeholder for get_topics method."""
            return []

# The GithubRepoRagTool implementation has been moved to trials.rag_component.tools.github_repo_rag_tool
# This removes duplication and ensures a single source of truth

class GithubRepoAnalysisAgents:
    """
    Specialized agents for GitHub repository analysis using RAG.
    """
    
    def __init__(self, llm="google", config=None):
        """
        Initialize GitHub repository analysis agents.
        
        Args:
            llm: LLM provider to use ('google', 'openai', 'anthropic')
            config: Configuration dict for the RAG tool
        """
        # Check required dependencies
        # if not HAS_CREWAI:
        #     raise ImportError("CrewAI is required. Run: pip install crewai crewai-tools")
        # if not HAS_EMBEDCHAIN:
        #     raise ImportError("Embedchain is required. Run: pip install embedchain")
            
        self.llm = llm
        
        # Process config if provided
        if config is None:
            config = {}
            
        # Create a default embedchain config if not provided
        if 'embedchain_config' not in config:
            config['embedchain_config'] = {
                "app": {
                    "name": "github-repo-analysis",
                    "config": {
                        "collect_metrics": False,
                    }
                },
                "llm": {
                    "provider": "google",
                    "config": {
                        "model": "gemini-2.0-flash",
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
                "chunker": {
                    "chunk_size": 1000,
                    "chunk_overlap": 200,
                    "length_function": "len",
                }
            }
            
        # Initialize the RAG tool with the provided config
        logger.info("Initializing GithubRepoRagTool with config")
        self.rag_tool = GithubRepoRagTool(config=config)
        
        # Simple response cache to avoid repeated API calls
        self._response_cache = {}
    
    def create_repo_analyzer_agent(self) -> Agent:
        """
        Create an agent specialized in analyzing repository structure.
        """
        return Agent(
            role="Repository Structure Analyzer",
            goal="Analyze the structure and organization of GitHub repositories",
            backstory="You are an expert in software architecture and repository organization. You analyze code repositories to understand their structure, identify key components, and evaluate their organization against best practices.",
            verbose=True,
            llm=self.llm,
            tools=[self.rag_tool],
            allow_delegation=False,
            memory=True,
            # Enable reasoning for better analysis
            reasoning=True,
            max_reasoning_attempts=2,
        )
    
    def create_code_insight_agent(self) -> Agent:
        """
        Create an agent specialized in code understanding and summarization.
        """
        return Agent(
            role="Code Insight Specialist",
            goal="Understand and summarize code functionality and implementation details",
            backstory="You are a senior software developer with expertise in multiple programming languages. Your specialty is reading code and explaining its functionality in clear, concise terms that anyone can understand.",
            verbose=True,
            llm=self.llm,
            tools=[self.rag_tool],
            allow_delegation=False,
            memory=True,
            reasoning=True,
            max_reasoning_attempts=2,
        )
    
    def create_architecture_agent(self) -> Agent:
        """
        Create an agent specialized in architecture and system design.
        """
        return Agent(
            role="Architecture Designer",
            goal="Analyze and explain system architecture and component interactions",
            backstory="You are a system architect with decades of experience designing scalable software systems. You can identify patterns, dependencies, and interactions between components in a codebase.",
            verbose=True,
            llm=self.llm,
            tools=[self.rag_tool],
            allow_delegation=False,
            memory=True,
            reasoning=True,
            max_reasoning_attempts=2,
        )
    
    def create_doc_generator_agent(self) -> Agent:
        """
        Create an agent specialized in generating documentation.
        """
        return Agent(
            role="Documentation Generator",
            goal="Create clear, comprehensive documentation from repository analysis",
            backstory="You are a technical writer with a background in software development. You excel at creating documentation that is both technically accurate and easy to understand.",
            verbose=True,
            llm=self.llm,
            tools=[self.rag_tool],
            allow_delegation=False,
            memory=True,
            reasoning=True,
            max_reasoning_attempts=2,
        )
    
    def create_mentor_agent(self) -> Agent:
        """
        Create an agent specialized in answering questions about the repository.
        """
        return Agent(
            role="Repository Guide",
            goal="Answer questions about the repository and guide new developers",
            backstory="You are a mentor who helps new developers understand codebases quickly. You provide clear explanations and point developers to the right files and components.",
            verbose=True,
            llm=self.llm,
            tools=[self.rag_tool],
            allow_delegation=False,
            memory=True,
            reasoning=True,
            max_reasoning_attempts=2,
        )
    
    def create_crew(self, repo_url: str) -> Crew:
        """
        Create a crew of agents for repository analysis.
        
        Args:
            repo_url: URL of the GitHub repository to analyze
            
        Returns:
            Crew: A CrewAI crew of agents
        """
        # Create agents
        repo_analyzer = self.create_repo_analyzer_agent()
        code_insight = self.create_code_insight_agent()
        architecture = self.create_architecture_agent()
        doc_generator = self.create_doc_generator_agent()
        mentor = self.create_mentor_agent()
        
        # Add repository to knowledge base
        logger.info(f"Adding repository to knowledge base: {repo_url}")
        success = self.rag_tool.add_github_repo(repo_url)
        if not success:
            logger.error(f"Failed to add repository {repo_url} to knowledge base")
        else:
            logger.info(f"Successfully added repository {repo_url} to knowledge base")
        
        # Create tasks
        analyze_structure_task = Task(
            description=f"Analyze the structure of the repository at {repo_url}. Identify main directories, key files, and overall organization.",
            expected_output="A comprehensive analysis of the repository structure, including main components and their organization.",
            agent=repo_analyzer,
            # Reasoning prompt for better analysis
            reasoning_prompt=(
                "Consider the following when analyzing the repository structure:\n"
                "1. What are the main directories and what purpose do they serve?\n"
                "2. How are the files organized?\n"
                "3. Does the structure follow common patterns for this type of project?\n"
                "4. What improvements could be made to the organization?"
            )
        )
        
        code_insight_task = Task(
            description="Analyze the code to understand the main functionality, implementation details, and code patterns.",
            expected_output="A detailed explanation of the codebase functionality, including key components and how they work.",
            agent=code_insight,
            context=[analyze_structure_task],
            reasoning_prompt=(
                "Consider the following when analyzing the code:\n"
                "1. What are the key functions and classes?\n"
                "2. What design patterns are being used?\n"
                "3. How is the code organized into modules?\n"
                "4. What external dependencies are being used and how?"
            )
        )
        
        architecture_task = Task(
            description="Analyze the system architecture, component interactions, and data flow.",
            expected_output="A clear explanation of the system architecture, including component interactions and data flow diagrams.",
            agent=architecture,
            context=[analyze_structure_task, code_insight_task],
            reasoning_prompt=(
                "Consider the following when analyzing the architecture:\n"
                "1. What are the main components and how do they interact?\n"
                "2. How does data flow through the system?\n"
                "3. What architectural patterns are being used?\n"
                "4. How scalable and maintainable is the current architecture?"
            )
        )
        
        documentation_task = Task(
            description="Generate comprehensive documentation for the repository, including setup instructions, architecture overview, and component details.",
            expected_output="Complete documentation in markdown format, including setup guides, architecture diagrams, and component explanations.",
            agent=doc_generator,
            context=[analyze_structure_task, code_insight_task, architecture_task],
            reasoning_prompt=(
                "Consider the following when creating documentation:\n"
                "1. What information would a new developer need to get started?\n"
                "2. How can the architecture be explained clearly?\n"
                "3. What details about each component should be included?\n"
                "4. What examples would help illustrate the system's functionality?"
            )
        )
        
        # Create crew
        crew = Crew(
            agents=[repo_analyzer, code_insight, architecture, doc_generator, mentor],
            tasks=[analyze_structure_task, code_insight_task, architecture_task, documentation_task],
            process=Process.sequential,
            verbose=True,
        )
        
        return crew

    def analyze_repository(self, repo_url: str) -> str:
        """
        Analyze a GitHub repository and provide comprehensive insights.
        
        Args:
            repo_url: URL of the GitHub repository to analyze
            
        Returns:
            str: Analysis results
        """
        try:
            # Create a cache key from the repo_url
            cache_key = f"{repo_url}::analysis"
            
            # Check if we have a cached response
            if hasattr(self, '_response_cache') and cache_key in self._response_cache:
                logger.info(f"Using cached analysis for {repo_url}")
                return self._response_cache[cache_key]
            
            # Add the repository first to check for any rate limit issues
            logger.info(f"Adding repository to knowledge base: {repo_url}")
            if not self.rag_tool.add_github_repo(repo_url):
                # If add_github_repo returns False, there was an error (likely rate limit)
                rate_limit_msg = "Error: Unable to process repository. GitHub API rate limit may have been exceeded. Please set GITHUB_TOKEN environment variable or wait before trying again."
                
                # For demo purposes, provide a sample analysis
                parts = repo_url.strip('/').split('/')
                if len(parts) >= 5:
                    repo_name = parts[4]
                else:
                    repo_name = "repository"
                    
                sample = f"""
# Analysis of {repo_name} Repository

## Repository Structure
The repository appears to follow a typical structure for its type of project:

- Core application code is likely in `/src` or `/app`
- Documentation in `/docs` or README files
- Configuration files in the root directory
- Tests in a `/tests` or `/spec` directory

## Key Components
Without direct access to the code due to rate limits, I can infer the following components:

- Main application entry points
- API or service layers
- Data models or schemas
- Utility functions and helpers

## Dependencies
The project likely depends on:

- Standard libraries for its language
- External packages for specific functionality
- Testing frameworks for validation

## Architecture
The architecture appears to follow industry standards for this type of application.

---
Note: This is a generalized analysis due to GitHub API rate limits. For a detailed analysis, please set the GITHUB_TOKEN environment variable and try again.
"""
                return f"{rate_limit_msg}\n\nHowever, here's a sample analysis for demonstration purposes:\n\n{sample}"
            
            # Create a crew for repository analysis
            logger.info(f"Creating crew for repository analysis: {repo_url}")
            crew = self.create_crew(repo_url)
            
            # Run the analysis
            logger.info(f"Running crew analysis for repository: {repo_url}")
            result = crew.kickoff()
            
            # Cache the response
            if hasattr(self, '_response_cache'):
                self._response_cache[cache_key] = result
                logger.info(f"Cached analysis results for repository: {repo_url}")
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing repository: {e}", exc_info=True)
            if "rate limit exceeded" in str(e).lower():
                return "Error: GitHub API rate limit exceeded. Please set GITHUB_TOKEN environment variable or wait before trying again."
            return f"Error analyzing repository: {str(e)}"
    
    def query_repository(self, repo_url: str, query: str) -> str:
        """
        Query information about a GitHub repository.
        
        Args:
            repo_url: URL of the GitHub repository
            query: Specific question about the repository
            
        Returns:
            str: Answer to the query
        """
        try:
            # Create a cache key from the repo_url and query
            cache_key = f"{repo_url}::{query}"
            
            # Check if we have a cached response
            if hasattr(self, '_response_cache') and cache_key in self._response_cache:
                logger.info(f"Using cached response for {repo_url}")
                return self._response_cache[cache_key]
            
            # Generate repo_id using hashlib
            repo_id = hashlib.md5(repo_url.encode()).hexdigest()
            logger.debug(f"Repository ID: {repo_id}")
            
            # Add the repository if not already in the knowledge base
            logger.info(f"Adding repository to knowledge base: {repo_url}")
            success = self.rag_tool.add_github_repo(repo_url)
            
            if not success:
                # If add_github_repo returns False, there was an error (likely rate limit)
                rate_limit_msg = "Error: Unable to process repository. GitHub API rate limit may have been exceeded. Please set GITHUB_TOKEN environment variable or wait before trying again."
                logger.error(rate_limit_msg)
                
                # For demo purposes, provide a sample response based on repo URL
                if "demo" in query.lower() or "sample" in query.lower():
                    sample = self._generate_sample_response(repo_url, query)
                    return f"{rate_limit_msg}\n\nHowever, here's a sample response for demonstration purposes:\n\n{sample}"
                
                return rate_limit_msg
            
            # Repository was successfully added, now query the knowledge base
            logger.info(f"Querying knowledge base with: {query}")
            
            # Check if the rag_tool has direct embedchain access
            if hasattr(self.rag_tool, '_direct_embedchain') and self.rag_tool._direct_embedchain:
                logger.info("Using direct EmbedchainApp for querying")
            else:
                logger.warning("Direct EmbedchainApp not available, may use fallback methods")
            
            try:
                # Run the query through the RAG tool
                logger.info(f"Running query through RAG tool: {query}")
                result = self.rag_tool.run(query)
                logger.info("Query completed successfully")
            except Exception as e:
                logger.error(f"Error querying repository: {e}", exc_info=True)
                # If the query fails, try using mock mode as fallback
                logger.warning("Switching to mock mode due to query error")
                if hasattr(self.rag_tool, 'mock_mode'):
                    self.rag_tool.mock_mode = True
                    logger.info("Using mock mode for response generation")
                    if hasattr(self.rag_tool, '_generate_mock_response'):
                        result = self.rag_tool._generate_mock_response(query)
                        logger.info("Generated mock response as fallback")
                    else:
                        result = f"Error querying repository: {str(e)}"
                else:
                    result = f"Error querying repository: {str(e)}"
            
            # Cache the response
            if hasattr(self, '_response_cache'):
                self._response_cache[cache_key] = result
                logger.info(f"Cached query result for '{query}' on repository: {repo_url}")
            
            return result
        except Exception as e:
            logger.error(f"Error querying repository: {e}", exc_info=True)
            if "rate limit exceeded" in str(e).lower():
                return "Error: GitHub API rate limit exceeded. Please set GITHUB_TOKEN environment variable or wait before trying again."
            return f"Error querying repository: {str(e)}"
    
    def _generate_sample_response(self, repo_url: str, query: str) -> str:
        """Generate a sample response for demo purposes when rate limits are hit."""
        # Extract repo name from URL
        parts = repo_url.strip('/').split('/')
        if len(parts) >= 5:
            repo_name = parts[4]
        else:
            repo_name = "repository"
            
        if "structure" in query.lower() or "organized" in query.lower():
            return f"""
The {repo_name} repository appears to be structured as follows:

1. **Core Components**:
   - Main application logic is likely in the `/src` or `/app` directory
   - API endpoints or services may be in `/api` or `/services`
   - Database models probably in `/models` or `/db`

2. **Frontend**:
   - If it has a frontend, it's likely in `/frontend`, `/client`, or `/ui`
   - UI components would be organized in a component hierarchy

3. **Documentation**:
   - README.md in the root provides an overview
   - Additional documentation may be in `/docs`

4. **Testing**:
   - Tests are likely in `/tests` or `/spec`
   - May include unit, integration, and e2e tests

5. **Configuration**:
   - Config files in the root or in a `/config` directory
   - Environment variables may be specified in `.env` files

This is a generalized structure based on common patterns and may not exactly match the actual repository.
"""
        
        elif "purpose" in query.lower() or "what is" in query.lower() or "about" in query.lower():
            return f"""
Based on the repository name "{repo_name}", this project appears to be related to:

- Possibly an agent-based system or intelligent assistant
- May involve AI/ML components
- Could be a tool for automation or information retrieval

Without accessing the actual code due to API rate limits, I can only provide this general assessment based on naming patterns and common project types.
"""
        
        else:
            return f"""
I don't have specific information about the {repo_name} repository due to GitHub API rate limits.

To answer this query accurately, I would need to analyze the repository code and structure. Please try again later or set the GITHUB_TOKEN environment variable to increase API rate limits.

The query was: "{query}"
"""


# Example usage
if __name__ == "__main__":
    try:
        # Check for required dependencies
        if not HAS_CREWAI:
            print("Error: CrewAI is required. Run: pip install crewai crewai-tools")
            exit(1)
        if not HAS_EMBEDCHAIN:
            print("Error: Embedchain is required. Run: pip install embedchain")
            exit(1)
        if not HAS_GITHUB:
            print("Error: PyGithub is required. Run: pip install PyGithub")
            exit(1)
            
        # Set Google AI API key
        if "GOOGLE_API_KEY" not in os.environ:
            print("Error: GOOGLE_API_KEY environment variable is required")
            print("Set it with: export GOOGLE_API_KEY=your-api-key")
            exit(1)
        
        # Initialize the agents
        repo_agents = GithubRepoAnalysisAgents(llm="google")
        
        # Analyze a repository
        repo_url = "https://github.com/vishnutejaa/Hack-Agent-Repo-IT"
        analysis = repo_agents.analyze_repository(repo_url)
        print(analysis)
        
        # Query specific information
        answer = repo_agents.query_repository(
            repo_url, 
            "What is the main purpose of this repository and how is it structured?"
        )
        print(answer)
    except ImportError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
