#!/usr/bin/env python3
"""
Example Usage of RAG Component

This script demonstrates how to use the RAG component in your Python code.
It provides examples of initializing the components, analyzing repositories,
and querying information.
"""

import os
import sys
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the RAG component
try:
    from rag_component import GithubRepoRagTool, GithubRepoAnalysisAgents
except ImportError:
    # Add the parent directory to sys.path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rag_component import GithubRepoRagTool, GithubRepoAnalysisAgents


def basic_usage_example():
    """
    Basic usage example of the RAG component.
    """
    print("\n=== Basic Usage Example ===\n")
    
    # Create an instance of the GitHub Repository Analysis Agents
    agents = GithubRepoAnalysisAgents(llm="google")
    
    # Define a repository URL
    repo_url = "https://github.com/vishnutejaa/Hack-Agent-Repo-IT"
    
    # Query information about the repository
    query = "What is the purpose of this repository?"
    print(f"Querying: {query}")
    answer = agents.query_repository(repo_url, query)
    print(f"\nAnswer:\n{answer}\n")


def advanced_usage_example():
    """
    Advanced usage example with custom configuration.
    """
    print("\n=== Advanced Usage Example ===\n")
    
    # Define custom configuration
    custom_config = {
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
    
    # Create the RAG tool with custom configuration
    rag_tool = GithubRepoRagTool(
        name="custom_github_knowledge",
        description="Custom GitHub repository knowledge tool",
        summarize=True,
        config=custom_config
    )
    
    # Add a repository
    repo_url = "https://github.com/vishnutejaa/Hack-Agent-Repo-IT"
    rag_tool.add_github_repo(repo_url)
    
    # Query the knowledge base directly
    query = "How is the code structured?"
    print(f"Querying: {query}")
    answer = rag_tool.run(query)
    print(f"\nAnswer:\n{answer}\n")


def multi_repo_example():
    """
    Example of using the RAG component with multiple repositories.
    """
    print("\n=== Multi-Repository Example ===\n")
    
    # Create an instance of the RAG tool
    rag_tool = GithubRepoRagTool()
    
    # Define repository URLs
    repo_urls = [
        "https://github.com/vishnutejaa/Hack-Agent-Repo-IT",
        "https://github.com/openai/openai-python",
        "https://github.com/google/generative-ai-python",
    ]
    
    # Add repositories
    for repo_url in repo_urls:
        print(f"Adding repository: {repo_url}")
        rag_tool.add_github_repo(repo_url, max_files=20)
    
    # Create agents using the configured RAG tool
    agents = GithubRepoAnalysisAgents(llm="google")
    agents.rag_tool = rag_tool
    
    # Query information about the repositories
    queries = [
        "Compare the structure of these repositories",
        "What are the main dependencies used in these projects?",
        "How do these repositories handle errors?"
    ]
    
    for query in queries:
        print(f"\nQuerying: {query}")
        # We'll use the first repository URL as the "primary" one for the query
        answer = agents.query_repository(repo_urls[0], query)
        print(f"\nAnswer:\n{answer}\n")


def integration_example():
    """
    Example of integrating the RAG component with other code.
    """
    print("\n=== Integration Example ===\n")
    
    class RepositoryAnalyzer:
        """
        Example class that uses the RAG component for repository analysis.
        """
        
        def __init__(self):
            """Initialize the repository analyzer."""
            self.agents = GithubRepoAnalysisAgents(llm="google")
            self.repositories = {}
            
        def add_repository(self, name: str, url: str) -> bool:
            """
            Add a repository for analysis.
            
            Args:
                name: Name for the repository
                url: URL of the GitHub repository
                
            Returns:
                bool: Success status
            """
            try:
                # Add repository to the RAG tool
                success = self.agents.rag_tool.add_github_repo(url)
                if success:
                    self.repositories[name] = url
                return success
            except Exception as e:
                logger.error(f"Error adding repository: {e}")
                return False
                
        def get_repo_info(self, name: str) -> Dict[str, Any]:
            """
            Get information about a repository.
            
            Args:
                name: Name of the repository
                
            Returns:
                Dict[str, Any]: Repository information
            """
            if name not in self.repositories:
                return {"error": f"Repository '{name}' not found"}
                
            url = self.repositories[name]
            
            # Get repository structure
            structure = self.agents.query_repository(url, "Describe the structure of this repository")
            
            # Get main features
            features = self.agents.query_repository(url, "What are the main features of this project?")
            
            # Get dependencies
            dependencies = self.agents.query_repository(url, "What are the main dependencies of this project?")
            
            return {
                "name": name,
                "url": url,
                "structure": structure,
                "features": features,
                "dependencies": dependencies
            }
            
        def compare_repositories(self, repo_names: List[str]) -> str:
            """
            Compare multiple repositories.
            
            Args:
                repo_names: List of repository names to compare
                
            Returns:
                str: Comparison result
            """
            if not all(name in self.repositories for name in repo_names):
                missing = [name for name in repo_names if name not in self.repositories]
                return f"Error: Repositories not found: {', '.join(missing)}"
                
            urls = [self.repositories[name] for name in repo_names]
            query = f"Compare the following repositories: {', '.join(repo_names)}"
            
            # Use the first URL as the "primary" one for the query
            return self.agents.query_repository(urls[0], query)
    
    # Use the example class
    analyzer = RepositoryAnalyzer()
    
    # Add repositories
    analyzer.add_repository("hack-agent", "https://github.com/vishnutejaa/Hack-Agent-Repo-IT")
    analyzer.add_repository("openai-python", "https://github.com/openai/openai-python")
    
    # Get repository information
    repo_info = analyzer.get_repo_info("hack-agent")
    print("Repository Information:")
    print(f"Name: {repo_info['name']}")
    print(f"URL: {repo_info['url']}")
    print(f"Structure:\n{repo_info['structure'][:500]}...")
    
    # Compare repositories
    comparison = analyzer.compare_repositories(["hack-agent", "openai-python"])
    print("\nRepository Comparison:")
    print(f"{comparison[:500]}...")


def main():
    """Main function to run the examples."""
    # Load environment variables
    load_dotenv()
    
    # Check for GitHub token
    if "GITHUB_TOKEN" not in os.environ:
        print("\n⚠️ Warning: No GitHub token found. API rate limits may be restrictive.")
        print("Consider setting the GITHUB_TOKEN environment variable for better results.")
    
    try:
        # Run examples
        basic_usage_example()
        advanced_usage_example()
        multi_repo_example()
        integration_example()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 