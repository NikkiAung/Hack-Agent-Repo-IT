import os
from typing import Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=False, env="API_RELOAD")
    
    # CORS Settings
    cors_origins: list = Field(default=["http://localhost:3000", "http://127.0.0.1:3000"], env="CORS_ORIGINS")
    
    # LLM API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Vector Database Settings
    weaviate_url: str = Field(default="http://localhost:8080", env="WEAVIATE_URL")
    weaviate_api_key: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")
    
    qdrant_url: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    
    # Graph Database Settings
    neo4j_uri: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", env="NEO4J_USER")
    neo4j_password: str = Field(default="password", env="NEO4J_PASSWORD")
    
    # PostgreSQL Settings (for future use)
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_db: str = Field(default="repo_analysis", env="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="password", env="POSTGRES_PASSWORD")
    
    # CrewAI Settings
    crew_memory_enabled: bool = Field(default=True, env="CREW_MEMORY_ENABLED")
    crew_verbose: bool = Field(default=True, env="CREW_VERBOSE")
    
    # Embedding Settings
    embedding_model: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")
    embedding_dimensions: int = Field(default=1536, env="EMBEDDING_DIMENSIONS")
    
    # Repository Analysis Settings
    max_repo_size_mb: int = Field(default=500, env="MAX_REPO_SIZE_MB")
    analysis_timeout_minutes: int = Field(default=30, env="ANALYSIS_TIMEOUT_MINUTES")
    
    # Logging Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    # Security Settings
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Validation functions
def validate_llm_config() -> bool:
    """Validate that at least one LLM API key is configured"""
    return bool(settings.openai_api_key or settings.anthropic_api_key)

def validate_vector_db_config() -> bool:
    """Validate vector database configuration"""
    return bool(settings.weaviate_url or settings.qdrant_url)

def get_database_url() -> str:
    """Get PostgreSQL database URL"""
    return f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

def get_neo4j_config() -> dict:
    """Get Neo4j configuration"""
    return {
        "uri": settings.neo4j_uri,
        "user": settings.neo4j_user,
        "password": settings.neo4j_password
    }

def get_weaviate_config() -> dict:
    """Get Weaviate configuration"""
    config = {"url": settings.weaviate_url}
    if settings.weaviate_api_key:
        config["api_key"] = settings.weaviate_api_key
    return config

def get_qdrant_config() -> dict:
    """Get Qdrant configuration"""
    config = {"url": settings.qdrant_url}
    if settings.qdrant_api_key:
        config["api_key"] = settings.qdrant_api_key
    return config