#!/usr/bin/env python3
"""
FastAPI Server Entry Point for Repository Analysis Platform

This is the main entry point for the FastAPI backend server.
It initializes the application with proper configuration and starts the server.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn
from backend.config import settings, validate_llm_config, validate_vector_db_config
from backend.api.main import app

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

def validate_configuration():
    """Validate application configuration before starting"""
    logger.info("Validating application configuration...")
    
    # Check LLM configuration
    if not validate_llm_config():
        logger.error("No LLM API key configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return False
    
    # Check vector database configuration
    if not validate_vector_db_config():
        logger.warning("No vector database configured. Some features may not work properly.")
    
    # Log configuration status
    logger.info(f"API will run on {settings.api_host}:{settings.api_port}")
    logger.info(f"CORS origins: {settings.cors_origins}")
    
    if settings.openai_api_key:
        logger.info("OpenAI API key configured")
    if settings.anthropic_api_key:
        logger.info("Anthropic API key configured")
    
    logger.info(f"Weaviate URL: {settings.weaviate_url}")
    logger.info(f"Neo4j URI: {settings.neo4j_uri}")
    
    return True

def main():
    """Main entry point"""
    logger.info("Starting Repository Analysis Platform API Server")
    
    # Validate configuration
    if not validate_configuration():
        logger.error("Configuration validation failed. Exiting.")
        sys.exit(1)
    
    # Start the server
    try:
        uvicorn.run(
            "backend.api.main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.api_reload,
            log_level=settings.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()