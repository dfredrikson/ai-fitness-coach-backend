"""
AI Fitness Coach - FastAPI Application

Entrenador personal inteligente con integración Strava y análisis IA.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.database import create_tables
from app.api.v1 import api_router

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Entrenador personal inteligente con integración Strava y análisis IA",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    create_tables()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if settings.debug else None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
