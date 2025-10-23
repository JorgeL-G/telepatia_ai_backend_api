from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.routers import health
from app.routers import message
from app.services.audio_service import AudioService
from app.services.google_genai_service import GoogleGenAIService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown events.
    """
    # Startup
    logger.info("Starting server...")
    if AudioService().load_audio_pipeline():
        logger.info("ASR model preloaded successfully")
    else:
        logger.warning("ASR model not preloaded, will use lazy loading")
    
    if GoogleGenAIService().initialize_client():
        logger.info("Google GenAI service initialized successfully")
    else:
        logger.warning("Google GenAI service not initialized, will use lazy loading")
    yield
    # Shutdown
    logger.info("Shutting down server...")


# Create FastAPI instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for capture, validation, storage, transcription and structuring of clinical information",
    debug=settings.debug,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(message.router)


@app.get("/")
async def root():
    """
    Root endpoint that provides basic API information.
    """
    return {
        "message": "Welcome to Telepatía AI Backend API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
