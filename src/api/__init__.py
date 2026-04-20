"""
API module for AI-ARB web interface
FastAPI REST API wrapper around ARBPipeline
"""

from src.api.main import create_app

__all__ = ["create_app"]
