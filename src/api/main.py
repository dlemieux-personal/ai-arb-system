"""
FastAPI Application Factory
Main entry point for the REST API
"""

import logging
from typing import Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from src.api.config import settings
from src.api.routes import router
from src.api.models import ErrorResponse

logger = logging.getLogger(__name__)


def create_app(config_override: Optional[dict] = None) -> FastAPI:
    """
    FastAPI application factory
    Creates and configures the FastAPI app with all middleware and routes
    
    Args:
        config_override: Optional dict to override settings (for testing)
    
    Returns:
        Configured FastAPI application instance
    """
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        docs_url=settings.docs_url if settings.enable_docs else None,
        redoc_url=settings.redoc_url if settings.enable_docs else None,
        openapi_url=settings.openapi_url if settings.enable_docs else None,
    )
    
    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        expose_headers=["X-Request-ID"],
        max_age=3600,
    )
    
    # Include API routes
    app.include_router(router)
    
    # Exception handlers
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors"""
        errors = exc.errors()
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "ValidationError",
                "message": "Invalid request data",
                "details": {
                    "errors": [
                        {
                            "field": ".".join(str(x) for x in error.get("loc", [])),
                            "message": error.get("msg", "validation error"),
                            "type": error.get("type", "unknown"),
                        }
                        for error in errors
                    ]
                },
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "details": {
                    "type": type(exc).__name__,
                } if settings.debug else {},
            },
        )
    
    # Startup event
    @app.on_event("startup")
    async def startup_event() -> None:
        """Application startup"""
        logger.info(f"Starting {settings.api_title} v{settings.api_version}")
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Debug: {settings.debug}")
        if settings.enable_github_auth:
            logger.info("GitHub OAuth2 authentication enabled")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Application shutdown"""
        logger.info(f"Shutting down {settings.api_title}")
    
    return app


# Create default app instance for direct uvicorn execution
app = create_app()
