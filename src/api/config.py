"""
API Configuration Module
Environment-driven settings for FastAPI application
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class APISettings(BaseSettings):
    """FastAPI configuration with environment variable support"""
    
    # API Metadata
    api_title: str = Field(default="AI Architecture Review Board API", alias="API_TITLE")
    api_version: str = Field(default="1.0.0", alias="API_VERSION")
    api_description: str = Field(
        default="REST API for submitting architectures and receiving AI-powered reviews",
        alias="API_DESCRIPTION"
    )
    
    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["GET", "POST"], alias="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(
        default=["Content-Type", "X-GitHub-Token"],
        alias="CORS_ALLOW_HEADERS"
    )
    
    # Authentication
    enable_github_auth: bool = Field(default=False, alias="ENABLE_GITHUB_AUTH")
    github_api_token_header: str = Field(default="X-GitHub-Token", alias="GITHUB_API_TOKEN_HEADER")
    github_api_endpoint: str = Field(default="https://api.github.com", alias="GITHUB_API_ENDPOINT")
    
    # Processing
    submission_timeout_seconds: int = Field(default=600, alias="SUBMISSION_TIMEOUT_SECONDS")
    max_submission_size_mb: int = Field(default=10, alias="MAX_SUBMISSION_SIZE_MB")
    
    # Documentation
    enable_docs: bool = Field(default=True, alias="ENABLE_DOCS")
    docs_url: str = Field(default="/api/docs", alias="DOCS_URL")
    redoc_url: str = Field(default="/api/redoc", alias="REDOC_URL")
    openapi_url: str = Field(default="/api/openapi.json", alias="OPENAPI_URL")
    
    # Server
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=1, alias="WORKERS")
    reload: bool = Field(default=True, alias="RELOAD")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables not defined in APISettings
        
    
def get_settings() -> APISettings:
    """Factory function to get API settings instance"""
    return APISettings()


# Global settings instance
settings = get_settings()
