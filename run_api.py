#!/usr/bin/env python
"""
FastAPI Server Entry Point
Run with: python run_api.py
"""

import uvicorn
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.config import settings


def run() -> None:
    """Start the FastAPI development server"""
    
    print(f"🚀 Starting {settings.api_title} v{settings.api_version}")
    print(f"📍 Environment: {settings.environment}")
    print(f"🔗 Server: http://{settings.host}:{settings.port}")
    
    if settings.enable_docs:
        print(f"📚 Swagger UI: http://{settings.host}:{settings.port}{settings.docs_url}")
        print(f"📖 ReDoc: http://{settings.host}:{settings.port}{settings.redoc_url}")
    
    print()
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    run()
