"""FastAPI application factory and configuration"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.core.dependencies import model_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown events.
    
    Handles:
    - Model initialization on startup
    - Cleanup on shutdown
    """
    # Startup
    print("🚀 Starting GAN Backend API...")
    try:
        model_manager.initialize()
        print("✅ Models loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load models: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🛑 Shutting down GAN Backend API...")
    model_manager.cleanup()
    print("✅ Cleanup completed")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI instance
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-ready API for conditional GAN image generation with CLIP text embeddings",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # Add middleware for CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(router)
    
    # Root endpoint
    @app.get(
        "/",
        summary="API Root",
        tags=["info"],
    )
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Welcome to GAN Backend API",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": f"{settings.API_PREFIX}/health",
            "generate": f"{settings.API_PREFIX}/generate",
        }
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
