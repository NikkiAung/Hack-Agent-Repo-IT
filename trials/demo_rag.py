#!/usr/bin/env python3
"""
RAG System Demo
Interactive demo showing how to use the RAG system with GitHub repositories and Gemini Flash 2.0
"""

import os
import sys
import logging
import argparse
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the RAG components
try:
    from trials.rag_component import GithubRepoAnalysisAgents
    from backend.services.rag_service import RAGService
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure the repository structure is correct and dependencies are installed.")
    sys.exit(1)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="RAG System Demo")
    parser.add_argument("--repo", type=str, help="URL of the GitHub repository to analyze")
    parser.add_argument("--query", type=str, help="Query to run against the repository")
    parser.add_argument("--token", type=str, help="GitHub API token (or set GITHUB_TOKEN env variable)")
    parser.add_argument("--gemini-key", type=str, help="Google Gemini API key (or set GOOGLE_API_KEY env variable)")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode even if dependencies are available")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--mode", type=str, choices=["repo", "general", "both"], default="both",
                       help="Mode to run: 'repo' for GitHub analysis, 'general' for general RAG, 'both' for both")
    return parser.parse_args()

async def github_repo_analysis(repo_url, query=None, github_token=None, gemini_key=None, mock=False, debug=False):
    """Run GitHub repository analysis."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("\n" + "=" * 80)
    print(" 🤖 GitHub Repository RAG Analysis 🤖 ".center(80))
    print("=" * 80)
    
    print(f"\n📊 Repository: {repo_url}")
    
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
    elif "GOOGLE_API_KEY" not in os.environ and "GEMINI_API_KEY" in os.environ:
        os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
    
    # Initialize agents with config
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
    
    if mock:
        print("\n⚠️ Running in mock mode. Responses will be generated from templates.")
        # Add force_mock flag to config
        config["force_mock"] = True
    
    # Initialize agents
    print("\n🧠 Initializing RAG agents...")
    print("\n🔄 RAG Pipeline Sequence:")
    print("  1. Initializing Gemini embeddings and LLM models")
    print("  2. Creating vector database for document storage")
    print("  3. Preparing to retrieve repository content")
    
    agents = GithubRepoAnalysisAgents(llm="google", config=config)
    
    try:
        # Add the repository to the knowledge base
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
            return
        
        print("\n✅ Repository successfully added to knowledge base")
        
        # Check if we're in mock mode
        if hasattr(agents.rag_tool, 'mock_mode') and agents.rag_tool.mock_mode:
            print("⚠️ Note: Running in mock mode. Responses will be generated from templates.")
        
        if query:
            # Run a single query
            print(f"\n🔍 Query: {query}")
            print("⏳ Processing query...")
            print("  - Retrieving relevant chunks from vector database")
            print("  - Formatting prompt with context")
            print("  - Sending to Gemini model for response generation")
            
            answer = agents.query_repository(repo_url, query)
            
            print("\n📝 Answer:")
            print("-" * 80)
            print(answer)
            print("-" * 80)
        else:
            # Interactive mode
            await interactive_github_repo_queries(agents, repo_url)
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if "rate limit" in str(e).lower():
            print("\nThis is likely due to GitHub API rate limits.")
            print("Set a GitHub token with --token or GITHUB_TOKEN environment variable.")

async def interactive_github_repo_queries(agents, repo_url):
    """Interactive mode for querying a GitHub repository."""
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
    
    while True:
        print("\n" + "-" * 80)
        print("📝 Select a query:")
        for i, query in enumerate(predefined_queries):
            print(f"  {i+1}. {query}")
        print("  0. Exit")
        
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
            answer = agents.query_repository(repo_url, query)
            
            print("\n📝 Answer:")
            print("-" * 80)
            print(answer)
            print("-" * 80)
            
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

async def general_rag_demo():
    """Demo the general RAG system with sample queries"""
    print("\n" + "="*80)
    print("🤖 GENERAL RAG SYSTEM DEMO - Powered by Gemini Flash 2.0".center(80))
    print("="*80)
    
    # Initialize RAG service
    print("\n🚀 Initializing RAG Service...")
    rag_service = RAGService()
    
    if rag_service.gemini_client:
        print("✅ Gemini Flash 2.0 is ready!")
    elif rag_service.anthropic_client:
        print("✅ Anthropic Claude is ready!")
    elif rag_service.openai_client:
        print("✅ OpenAI GPT is ready!")
    else:
        print("❌ No LLM available")
        return
    
    # Sample queries to demonstrate the system
    sample_queries = [
        "What programming languages and frameworks are commonly used in modern web development?",
        "Explain the difference between REST and GraphQL APIs",
        "What are the best practices for database design?",
        "How does authentication work in web applications?",
        "What is the purpose of containerization with Docker?"
    ]
    
    print("\n📝 Running sample queries...")
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n{'-'*50}")
        print(f"Query {i}: {query}")
        print(f"{'-'*50}")
        
        try:
            response = await rag_service.query(query=query, max_results=3)
            
            if response and "answer" in response:
                answer = response["answer"]
                sources = response.get("sources", [])
                
                print(f"\n🤖 Answer:")
                print(answer)
                print(f"\n📚 Sources used: {len(sources)}")
                
                if sources:
                    for j, source in enumerate(sources[:2], 1):  # Show first 2 sources
                        print(f"   {j}. {source.get('type', 'Unknown')} - {source.get('module_name', 'N/A')}")
            else:
                print("❌ No response received")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*80)
    print("✅ Demo completed! The RAG system is working with Gemini Flash 2.0")
    print("="*80)

async def interactive_general_rag():
    """Interactive mode for custom general RAG queries"""
    print("\n🎯 GENERAL RAG INTERACTIVE MODE")
    print("Type your questions and get AI-powered answers!")
    print("Type 'quit' to exit.\n")
    
    rag_service = RAGService()
    
    while True:
        try:
            query = input("❓ Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not query:
                continue
                
            print("\n🤖 Thinking...")
            response = await rag_service.query(query=query, max_results=5)
            
            if response and "answer" in response:
                answer = response["answer"]
                sources = response.get("sources", [])
                
                print(f"\n💡 Answer:")
                print(answer)
                print(f"\n📊 Based on {len(sources)} sources\n")
            else:
                print("❌ Sorry, I couldn't generate an answer.\n")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")

async def main():
    """Main demo function"""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_args()
    
    # Set debug mode if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('trials.rag_component').setLevel(logging.DEBUG)
        logging.getLogger('backend.services').setLevel(logging.DEBUG)
    
    try:
        # Handle Gemini API key
        if args.gemini_key:
            os.environ["GOOGLE_API_KEY"] = args.gemini_key
        
        if args.mode in ["repo", "both"] and args.repo:
            # Run GitHub repository analysis
            await github_repo_analysis(
                repo_url=args.repo,
                query=args.query,
                github_token=args.token,
                gemini_key=args.gemini_key,
                mock=args.mock,
                debug=args.debug
            )
        
        if args.mode in ["general", "both"]:
            # Run general RAG demo
            if args.query:
                # Single query mode
                print("\n" + "="*80)
                print("🤖 GENERAL RAG QUERY".center(80))
                print("="*80)
                
                rag_service = RAGService()
                print(f"\n🔍 Query: {args.query}")
                print("⏳ Processing...")
                
                response = await rag_service.query(query=args.query, max_results=5)
                
                if response and "answer" in response:
                    answer = response["answer"]
                    sources = response.get("sources", [])
                    
                    print(f"\n💡 Answer:")
                    print(answer)
                    print(f"\n📊 Based on {len(sources)} sources\n")
                else:
                    print("❌ Sorry, I couldn't generate an answer.\n")
            else:
                # No query specified, run interactive demo
                await general_rag_demo()
                await interactive_general_rag()
        
        # If no mode or repo specified, show menu
        if not args.mode or (args.mode == "repo" and not args.repo):
            print("🚀 Welcome to the RAG System Demo!")
            print("\nChoose an option:")
            print("1. Run GitHub repository analysis")
            print("2. Run general RAG system demo")
            print("3. Both")
            
            choice = input("\nEnter your choice (1/2/3): ").strip()
            
            if choice == "1":
                repo_url = input("Enter GitHub repository URL: ").strip()
                if repo_url:
                    await github_repo_analysis(repo_url)
            elif choice == "2":
                await general_rag_demo()
                await interactive_general_rag()
            elif choice == "3":
                repo_url = input("Enter GitHub repository URL: ").strip()
                if repo_url:
                    await github_repo_analysis(repo_url)
                await general_rag_demo()
                await interactive_general_rag()
            else:
                print("Invalid choice. Running general RAG demo...")
                await general_rag_demo()
                await interactive_general_rag()
    
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 