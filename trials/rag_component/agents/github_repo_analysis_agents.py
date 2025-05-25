"""
GitHub Repository Analysis Agents

This module provides specialized agents for analyzing GitHub repositories
using CrewAI and the GithubRepoRagTool.
"""

import os
import logging
import hashlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Local imports
from ..utils.dependencies import DependencyManager, DEPENDENCY_STATUS
from ..tools.github_repo_rag_tool import GithubRepoRagTool

# Set up logging
logger = logging.getLogger(__name__)

# Import dependencies or use placeholders
if DEPENDENCY_STATUS['crewai']:
    from crewai import Agent, Task, Crew, Process
else:
    placeholders = DependencyManager.get_placeholder_classes()
    Agent = placeholders.get('Agent')
    Task = placeholders.get('Task')
    Crew = placeholders.get('Crew')
    Process = placeholders.get('Process')


class GithubRepoAnalysisAgents:
    """
    Specialized agents for GitHub repository analysis using RAG.
    """
    
    def __init__(self, llm="google", config: Optional[Dict[str, Any]] = None):
        """
        Initialize GitHub repository analysis agents.
        
        Args:
            llm: LLM provider to use ('google', 'openai', 'anthropic')
            config: Optional configuration for the RAG tool
        """
        # Check dependencies
        self.dependencies_available = all([
            DEPENDENCY_STATUS['crewai'],
            DEPENDENCY_STATUS['embedchain'],
            DEPENDENCY_STATUS['github']
        ])
        
        if not self.dependencies_available:
            logger.warning("Some dependencies are missing. Functionality will be limited.")
            for dep, status in DEPENDENCY_STATUS.items():
                if not status:
                    logger.warning(f"Missing dependency: {dep}")
        
        # Process configuration
        if config is None:
            config = {}
            
        # Check if force_mock is specified
        force_mock = config.pop('force_mock', False)
        if force_mock:
            logger.info("Force mock mode enabled through configuration")
            
        # Create a clean config for the RAG tool
        rag_config = config.copy()
        if force_mock:
            # Add a special flag to the rag_config to force mock mode
            rag_config['force_mock'] = True
            
        # Ensure embedchain_config is properly structured
        if 'embedchain_config' not in rag_config:
            # If embedchain_config doesn't exist, but some config keys are provided directly,
            # wrap them in an embedchain_config key
            embedded_keys = ['app', 'llm', 'embedder', 'chunker']
            has_embedded_keys = any(key in rag_config for key in embedded_keys)
            
            if has_embedded_keys:
                embedchain_config = {}
                # Move any embedchain-related keys to the embedchain_config
                for key in embedded_keys:
                    if key in rag_config:
                        embedchain_config[key] = rag_config.pop(key)
                
                # Add the wrapped config
                rag_config['embedchain_config'] = embedchain_config
            else:
                # No embedded keys, create a default embedchain_config
                rag_config['embedchain_config'] = {
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
        
        # Store parameters
        self.llm = llm
        self.config = config
        
        # Log the configuration we're using
        logger.debug(f"Initializing GithubRepoRagTool with config: {rag_config}")
        
        # Initialize RAG tool
        self.rag_tool = GithubRepoRagTool(config=rag_config)
        
        # If force_mock is True, ensure the RAG tool is in mock mode
        if force_mock and hasattr(self.rag_tool, 'mock_mode'):
            self.rag_tool.mock_mode = True
        
        # Simple response cache to avoid repeated API calls
        self._response_cache = {}
        
    def create_repo_analyzer_agent(self) -> Agent:
        """
        Create an agent specialized in analyzing repository structure.
        
        Returns:
            Agent: A CrewAI agent for repository structure analysis
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
            reasoning=True,
            max_reasoning_attempts=2,
        )
    
    def create_code_insight_agent(self) -> Agent:
        """
        Create an agent specialized in code understanding and summarization.
        
        Returns:
            Agent: A CrewAI agent for code insight
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
        
        Returns:
            Agent: A CrewAI agent for architecture analysis
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
        
        Returns:
            Agent: A CrewAI agent for documentation generation
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
        
        Returns:
            Agent: A CrewAI agent for mentoring and guidance
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
        self.rag_tool.add_github_repo(repo_url)
        
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
            if not self.rag_tool.add_github_repo(repo_url):
                # If add_github_repo returns False, there was an error (likely rate limit)
                return "Error: Unable to process repository. GitHub API rate limit may have been exceeded. Please set GITHUB_TOKEN environment variable or wait before trying again."
            
            # Check if CrewAI is available
            if not DEPENDENCY_STATUS['crewai']:
                logger.warning("CrewAI not available. Using mock response.")
                repo_name = repo_url.split('/')[-1] if '/' in repo_url else repo_url
                from ..utils.mock_responses import MockResponseGenerator
                mock_response = f"""
# Analysis of {repo_name} Repository

## Repository Structure
{MockResponseGenerator.generate_structure_response(repo_name)}

## Code Insights
The codebase appears to implement core functionality through a well-structured approach.

## Architecture
The system architecture follows standard patterns for this type of project.

## Documentation
This is a generated mock response because CrewAI is not available.
"""
                # Cache the response
                if hasattr(self, '_response_cache'):
                    self._response_cache[cache_key] = mock_response
                return mock_response
            
            # Create a crew for repository analysis
            crew = self.create_crew(repo_url)
            
            # Run the analysis
            result = crew.kickoff()
            
            # Cache the response
            if hasattr(self, '_response_cache'):
                self._response_cache[cache_key] = result
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing repository: {e}")
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
            
            logger.debug(f"Processing query for repository {repo_url}: {query}")
            logger.debug(f"Repository ID: {repo_id}")
            
            # Check if we're in mock mode
            if hasattr(self.rag_tool, 'mock_mode') and self.rag_tool.mock_mode:
                logger.info(f"RAG tool is in mock mode, will provide simulated responses")
            
            # Add the repository if not already in the knowledge base
            # We don't need to check if it's in _processed_repos, add_github_repo will handle that
            logger.info(f"Adding repository to knowledge base: {repo_url}")
            success = self.rag_tool.add_github_repo(repo_url)
            
            if not success:
                # If add_github_repo returns False, there was an error (likely rate limit)
                rate_limit_msg = "Error: Unable to process repository. GitHub API rate limit may have been exceeded. Please set GITHUB_TOKEN environment variable or wait before trying again."
                logger.error(rate_limit_msg)
                
                # For demo purposes, provide a sample response based on repo URL
                if "demo" in query.lower() or "sample" in query.lower():
                    repo_name = repo_url.split('/')[-1] if '/' in repo_url else repo_url
                    from ..utils.mock_responses import MockResponseGenerator
                    if "structure" in query.lower():
                        sample = MockResponseGenerator.generate_structure_response(repo_name)
                    elif "code" in query.lower() or "example" in query.lower():
                        sample = MockResponseGenerator.generate_code_sample_response(repo_name)
                    else:
                        sample = MockResponseGenerator.generate_generic_response(repo_name, query)
                    return f"{rate_limit_msg}\n\nHowever, here's a sample response for demonstration purposes:\n\n{sample}"
                
                return rate_limit_msg
            
            # Query the knowledge base
            logger.info(f"Repository added successfully, querying with: {query}")
            
            # Check if the EmbedchainApp is properly initialized
            if hasattr(self.rag_tool, '_direct_embedchain') and self.rag_tool._direct_embedchain:
                logger.info("Using direct EmbedchainApp for querying")
            else:
                logger.warning("Direct EmbedchainApp not available, may use fallback methods")
                
            # Run the query
            try:
                result = self.rag_tool.run(query)
                logger.info("Query successful")
            except Exception as e:
                logger.error(f"Error running query through rag_tool.run: {e}")
                # If we get an error but the tool has a mock mode, try to get a mock response
                if hasattr(self.rag_tool, 'mock_mode'):
                    self.rag_tool.mock_mode = True
                    logger.info("Switching to mock mode due to query error")
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
            
            return result
        except Exception as e:
            logger.error(f"Error querying repository: {e}", exc_info=True)
            if "rate limit exceeded" in str(e).lower():
                return "Error: GitHub API rate limit exceeded. Please set GITHUB_TOKEN environment variable or wait before trying again."
            return f"Error querying repository: {str(e)}" 