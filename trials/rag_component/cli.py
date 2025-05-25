#!/usr/bin/env python3
"""
Command Line Interface for GitHub Repository RAG Tool

This module provides a command-line interface for the GitHub Repository
RAG tools and agents.
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any, Optional
import json
from datetime import datetime
from dotenv import load_dotenv

# Local imports
from .agents.github_repo_analysis_agents import GithubRepoAnalysisAgents
from .utils.dependencies import DependencyManager, DEPENDENCY_STATUS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="GitHub Repository RAG Tool")
    
    # Add main arguments
    parser.add_argument("--repo", type=str, required=True, help="URL of the GitHub repository to analyze")
    
    # Create a mutually exclusive group for analyze and query
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--analyze", action="store_true", help="Run a full repository analysis")
    group.add_argument("--query", type=str, help="Specific question to ask about the repository")
    
    # Add optional arguments
    parser.add_argument("--config", type=str, help="Path to configuration file (JSON)")
    parser.add_argument("--output", type=str, help="Path to output file (default: stdout)")
    parser.add_argument("--llm", type=str, default="google", choices=["google", "openai", "anthropic"], help="LLM provider to use")
    parser.add_argument("--github-token", type=str, help="GitHub API token (or set GITHUB_TOKEN in .env)")
    
    # Add debug options
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies and exit")
    
    return parser.parse_args()


def setup_environment(args: argparse.Namespace) -> None:
    """
    Set up environment variables and configuration.
    
    Args:
        args: Command line arguments
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Set GitHub token if provided
    if args.github_token:
        os.environ["GITHUB_TOKEN"] = args.github_token
        
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Log dependency status
    logger.info("Dependency status:")
    for dep, status in DEPENDENCY_STATUS.items():
        logger.info(f"  {dep}: {'Available' if status else 'Not available'}")


def load_config(config_path: Optional[str]) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    if not config_path:
        return {}
        
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {}


def validate_repository_url(repo_url: str) -> str:
    """
    Validate and clean the repository URL format.
    
    Args:
        repo_url: Repository URL
        
    Returns:
        str: Cleaned repository URL
    """
    # Fix common URL errors like double https://
    if "https://https://" in repo_url:
        repo_url = repo_url.replace("https://https://", "https://")
    
    # Ensure URL has proper format
    parts = repo_url.strip('/').split('/')
    if len(parts) < 5 or parts[2] != 'github.com':
        raise ValueError(f"Invalid GitHub URL: {repo_url}. Format should be: https://github.com/owner/repo")
    
    # Return the cleaned URL
    return repo_url


def write_output(content: str, output_path: Optional[str]) -> None:
    """
    Write output to file or stdout.
    
    Args:
        content: Content to write
        output_path: Path to output file (None for stdout)
    """
    if output_path:
        try:
            with open(output_path, 'w') as f:
                f.write(content)
            logger.info(f"Output written to {output_path}")
        except Exception as e:
            logger.error(f"Error writing output: {e}")
            print(content)
    else:
        print(content)


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        int: Exit code
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Set up environment
        setup_environment(args)
        
        # Check dependencies and exit if requested
        if args.check_deps:
            for dep, status in DEPENDENCY_STATUS.items():
                print(f"{dep}: {'Available' if status else 'Not available'}")
            return 0
            
        # Validate repository URL
        repo_url = validate_repository_url(args.repo)
        
        # Load configuration
        config = load_config(args.config)
        
        # Print header
        print(f"🚀 GitHub Repository RAG Tool")
        print(f"📦 Repository: {repo_url}")
        
        # Check for GitHub token
        if "GITHUB_TOKEN" not in os.environ:
            print("\n⚠️ Warning: No GitHub token found. API rate limits may be restrictive.")
            print("Consider setting the GITHUB_TOKEN environment variable for better results.")
        
        # Initialize agents
        print(f"\n🤖 Initializing GitHub Repository RAG Agents with {args.llm.capitalize()}...")
        repo_agents = GithubRepoAnalysisAgents(llm=args.llm, config=config)
        
        # Run the appropriate action
        if args.analyze:
            print("\n📊 Running full repository analysis...")
            print("⏳ This may take a few minutes depending on the repository size...")
            
            result = repo_agents.analyze_repository(repo_url)
            
            if "rate limit exceeded" in result.lower():
                print("\n❌ GitHub API rate limit exceeded!")
                print("Please set GITHUB_TOKEN environment variable or wait before trying again.")
            
            print("\n📝 Analysis Results:")
            print("=" * 80)
            # Write output
            write_output(result, args.output)
            if not args.output:
                print("=" * 80)
            
        elif args.query:
            print(f"\n❓ Querying: {args.query}")
            print("⏳ Retrieving information...")
            
            answer = repo_agents.query_repository(repo_url, args.query)
            
            if "rate limit exceeded" in answer.lower():
                print("\n❌ GitHub API rate limit exceeded!")
                print("Please set GITHUB_TOKEN environment variable or wait before trying again.")
            
            print("\n📝 Answer:")
            print("=" * 80)
            # Write output
            write_output(answer, args.output)
            if not args.output:
                print("=" * 80)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
        return 130  # Standard exit code for SIGINT
    except ValueError as e:
        print(f"\n\n❌ Configuration Error: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 