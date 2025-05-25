"""
RAG Component for GitHub Repository Analysis

This package provides tools and agents for analyzing GitHub repositories
using Retrieval Augmented Generation (RAG) with Gemini 2.0 Flash.
"""

from .tools.github_repo_rag_tool import GithubRepoRagTool
from .agents.github_repo_analysis_agents import GithubRepoAnalysisAgents

__version__ = "0.1.0" 