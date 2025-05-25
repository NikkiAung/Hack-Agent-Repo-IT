#!/usr/bin/env python3
"""
Demo Script for GitHub Repository RAG

This is a simple demo script for analyzing and querying GitHub repositories
using the RAG component.
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Set specific logger levels
logging.getLogger('trials.rag_component').setLevel(logging.INFO)
logger = logging.getLogger(__name__)

# Import the RAG component
try:
    from trials.rag_component import GithubRepoAnalysisAgents
except ImportError:
    # Add the parent directory to sys.path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from trials.rag_component import GithubRepoAnalysisAgents
    except ImportError:
        print("Error: Could not import RAG component. Make sure it's installed correctly.")
        sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="GitHub Repository RAG Demo")
    parser.add_argument("--repo", type=str, default="https://github.com/vishnutejaa/Hack-Agent-Repo-IT",
                        help="URL of the GitHub repository to analyze")
    parser.add_argument("--query", type=str, 
                        help="Query to run (if not provided, will use a demo set of queries)")
    parser.add_argument("--token", type=str, help="GitHub API token (or set GITHUB_TOKEN env variable)")
    parser.add_argument("--gemini-key", type=str, help="Google Gemini API key (or set GOOGLE_API_KEY env variable)")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode even if dependencies are available")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def interactive_demo(repo_url, github_token=None, gemini_key=None, force_mock=False, debug=False):
    """Run an interactive demo."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('trials.rag_component').setLevel(logging.DEBUG)
    
    print("\n" + "=" * 80)
    print(" 🤖 GitHub Repository RAG Demo 🤖 ".center(80))
    print("=" * 80)
    
    print(f"\n📊 Repository: {repo_url}")
    
    # Check for GitHub token
    if not github_token and "GITHUB_TOKEN" not in os.environ:
        print("\n⚠️ Warning: No GitHub token found. API rate limits may be restrictive.")
        print("Consider setting the GITHUB_TOKEN environment variable for better results.")
        print("GitHub API allows only 60 requests per hour without authentication.")
    else:
        token_source = "argument" if github_token else "environment variable"
        print(f"\n✅ GitHub token found from {token_source}. This allows higher API rate limits.")
        print("Authenticated users can make up to 5,000 requests per hour.")
    
    # Set up the agents
    print("\n🧠 Initializing RAG agents...")
    
    # Handle GitHub token
    if github_token:
        # Set the token in the environment so the RAG tool can use it
        os.environ["GITHUB_TOKEN"] = github_token
        print("GitHub token set for the current session.")
        
    # Handle Gemini key
    if gemini_key:
        os.environ["GOOGLE_API_KEY"] = gemini_key
        print("Gemini API key set for the current session.")
    
    # Initialize agents with config
    # Create a comprehensive config for optimal performance
    config = {
        "embedchain_config": {  # Wrap in embedchain_config key
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
    }
    
    if force_mock:
        print("\n⚠️ Running in mock mode. Responses will be generated from templates.")
        # Create a config that will force mock mode
        config["force_mock"] = True
    
    print("\n🔄 RAG Pipeline Sequence:")
    print("  1. Initializing Gemini embeddings and LLM models")
    print("  2. Creating agents for repository analysis")
    print("  3. Setting up vector database for document storage")
    print("  4. Preparing to retrieve repository content")
    
    # Initialize agents
    agents = GithubRepoAnalysisAgents(llm="google", config=config)
    
    # Add the repository
    print(f"\n📦 Adding repository to knowledge base: {repo_url}")
    print("  - Retrieving repository structure")
    print("  - Downloading priority files (README, documentation)")
    print("  - Processing code files")
    print("  - Generating embeddings and storing in vector database")
    
    success = agents.rag_tool.add_github_repo(repo_url)
    
    if not success:
        print("\n❌ Failed to add repository.")
        print("  - Check your GitHub token and network connection")
        print("  - Ensure the repository URL is correct and accessible")
        print("  - You might have hit GitHub API rate limits")
    else:
        print("\n✅ Repository successfully added to knowledge base")
        # Check if we're in mock mode
        if hasattr(agents.rag_tool, 'mock_mode') and agents.rag_tool.mock_mode:
            print("⚠️ Note: Running in mock mode. Responses will be generated from templates.")
        else:
            # Verify the vector database has data
            print("✅ Vector database initialized and populated with repository data")
    
    # Query options
    predefined_queries = [
        "What is the purpose of this repository?",
        "How is the code structured?",
        "What are the main components?",
        "Show me some code examples",
        "What are the dependencies?",
        "How can I contribute to this project?",
        "What's the recommended way to use this code?",
        "Custom query (enter your own)"
    ]
    
    # Interactive loop
    while True:
        print("\n" + "-" * 80)
        print("📝 Select a query:")
        for i, query in enumerate(predefined_queries):
            print(f"  {i+1}. {query}")
        print("  0. Exit")
        
        # Get user choice
        try:
            choice = input("\nEnter choice (0-8): ")
            choice = int(choice)
            
            if choice == 0:
                print("\n👋 Thanks for trying the GitHub Repository RAG Demo!")
                break
            
            if choice < 0 or choice > len(predefined_queries):
                print(f"\n❌ Invalid choice. Please enter a number between 0 and {len(predefined_queries)}.")
                continue
            
            if choice == len(predefined_queries):
                # Custom query
                query = input("\nEnter your query: ")
                if not query.strip():
                    print("\n❌ Query cannot be empty.")
                    continue
            else:
                query = predefined_queries[choice-1]
            
            print(f"\n🔍 Querying: {query}")
            print("⏳ RAG Pipeline Process:")
            print("  1. Analyzing query")
            print("  2. Retrieving relevant chunks from vector database")
            print("  3. Formatting prompt with context")
            print("  4. Sending to Gemini model for response generation")
            
            # Run the query
            try:
                logger.info(f"Sending query to RAG pipeline: '{query}'")
                answer = agents.query_repository(repo_url, query)
                logger.info("Query completed successfully")
                
                print("\n📝 Answer:")
                print("-" * 80)
                print(answer)
                print("-" * 80)
                
                # Check if the response indicates an error with the vector database
                if "error" in answer.lower() and ("vector" in answer.lower() or "database" in answer.lower() or "embedding" in answer.lower()):
                    print("\n⚠️ There might be an issue with the vector database. The response indicates an error.")
                    print("  - This could be due to API rate limits")
                    print("  - The embeddings might not have been generated correctly")
                    print("  - The LLM might be having trouble processing the context")
                
            except Exception as e:
                logger.error(f"Error querying repository: {e}", exc_info=True)
                print(f"\n❌ Error querying repository: {str(e)}")
                print("Trying to continue with the demo despite the error...")
            
            # Check if user wants to continue
            cont = input("\nDo you want to try another query? (y/n): ")
            if cont.lower() != 'y':
                print("\n👋 Thanks for trying the GitHub Repository RAG Demo!")
                break
                
        except ValueError:
            print("\n❌ Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Thanks for trying the GitHub Repository RAG Demo!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


def single_query_demo(repo_url, query, github_token=None, gemini_key=None, force_mock=False, debug=False):
    """Run a single query demo."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('trials.rag_component').setLevel(logging.DEBUG)
    
    print("\n" + "=" * 80)
    print(" 🤖 GitHub Repository RAG Demo 🤖 ".center(80))
    print("=" * 80)
    
    print(f"\n📊 Repository: {repo_url}")
    print(f"🔍 Query: {query}")
    
    # Check for GitHub token
    if not github_token and "GITHUB_TOKEN" not in os.environ:
        print("\n⚠️ Warning: No GitHub token found. API rate limits may be restrictive.")
        print("GitHub API allows only 60 requests per hour without authentication.")
    else:
        token_source = "argument" if github_token else "environment variable"
        print(f"\n✅ GitHub token found from {token_source}. This allows higher API rate limits.")
        print("Authenticated users can make up to 5,000 requests per hour.")
    
    # Handle GitHub token
    if github_token:
        os.environ["GITHUB_TOKEN"] = github_token
        print("GitHub token set for the current session.")
        
    # Handle Gemini key
    if gemini_key:
        os.environ["GOOGLE_API_KEY"] = gemini_key
        print("Gemini API key set for the current session.")
    
    # Initialize agents with config
    # Create a comprehensive config for optimal performance
    config = {
        "embedchain_config": {  # Wrap in embedchain_config key
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
    }
    
    if force_mock:
        print("\n⚠️ Running in mock mode. Responses will be generated from templates.")
        # Create a config that will force mock mode
        config["force_mock"] = True
    
    # Initialize agents
    print("\n🧠 Initializing RAG agents...")
    print("\n🔄 RAG Pipeline Sequence:")
    print("  1. Initializing Gemini embeddings and LLM models")
    print("  2. Creating vector database for document storage")
    print("  3. Preparing to retrieve repository content")
    
    agents = GithubRepoAnalysisAgents(llm="google", config=config)
    
    try:
        print("\n⏳ Processing repository and retrieving information...")
        print("  - Fetching repository content via GitHub API")
        print("  - Generating embeddings with Gemini text-embedding-004")
        print("  - Storing vectors in local database")
        
        # Add the repository to the knowledge base
        success = agents.rag_tool.add_github_repo(repo_url)
        
        if not success:
            print("\n❌ Failed to add repository.")
            print("  - Check your GitHub token and network connection")
            print("  - Ensure the repository URL is correct and accessible")
            print("  - You might have hit GitHub API rate limits")
            return
            
        print("\n✅ Repository successfully added to knowledge base")
        
        # Check if we're in mock mode
        if hasattr(agents.rag_tool, 'mock_mode') and agents.rag_tool.mock_mode:
            print("⚠️ Note: Running in mock mode. Responses will be generated from templates.")
        else:
            # Verify the vector database has data
            print("✅ Vector database initialized and populated with repository data")
        
        print("  - Retrieving relevant chunks for your query")
        print("  - Sending query with context to Gemini 2.0 Flash")
        
        # Run the query with better error handling
        try:
            logger.info(f"Sending query to RAG pipeline: '{query}'")
            answer = agents.query_repository(repo_url, query)
            logger.info("Query completed successfully")
            
            print("\n📝 Answer:")
            print("-" * 80)
            print(answer)
            print("-" * 80)
            
            # Check if the response indicates an error with the vector database
            if "error" in answer.lower() and ("vector" in answer.lower() or "database" in answer.lower() or "embedding" in answer.lower()):
                print("\n⚠️ There might be an issue with the vector database. The response indicates an error.")
                print("  - This could be due to API rate limits")
                print("  - The embeddings might not have been generated correctly")
                print("  - The LLM might be having trouble processing the context")
                
        except Exception as e:
            logger.error(f"Error querying repository: {e}", exc_info=True)
            print(f"\n❌ Error querying repository: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error processing repository: {e}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        if "rate limit" in str(e).lower():
            print("\nThis is likely due to GitHub API rate limits.")
            print("Set a GitHub token with --token or GITHUB_TOKEN environment variable.")


def main():
    """Main function to run the demo."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_args()
    
    try:
        if args.query:
            # Run single query demo
            single_query_demo(
                args.repo, 
                args.query, 
                args.token, 
                args.gemini_key, 
                args.mock, 
                args.debug
            )
        else:
            # Run interactive demo
            interactive_demo(
                args.repo, 
                args.token,
                args.gemini_key, 
                args.mock, 
                args.debug
            )
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for trying the GitHub Repository RAG Demo!")
        return 1
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        print(f"\n\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())