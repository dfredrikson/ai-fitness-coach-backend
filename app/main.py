"""
AI Fitness Coach - FastAPI Application

Entrenador personal inteligente con integración Strava y análisis IA.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import os

from app.config import get_settings
from app.core.database import create_tables
from app.api.v1 import api_router
from app.scheduler import start_scheduler

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
    allow_origins=[
        "https://ai-fitness-coach-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    create_tables()
    start_scheduler()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve static files from the build directory
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Serve static files from the build directory
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Configurable frontend path
# Priority:
# 1. FRONTEND_BUILD_DIR env var
# 2. ./static (bundled in the backend repo for production)
# 3. ../../ai-fitness-coach-frontend/dist (local development sibling repo)

frontend_path = os.getenv("FRONTEND_BUILD_DIR")

if not frontend_path:
    # Check for bundled static folder in current directory
    bundled_path = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(bundled_path):
        frontend_path = bundled_path
    else:
        # Fallback to local sibling development path
        frontend_path = "../../ai-fitness-coach-frontend/dist"

frontend_path = os.path.abspath(frontend_path)

# Mount assets if directory exists
assets_path = os.path.join(frontend_path, "assets")
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
else:
    print(f"WARNING: Assets directory not found at {assets_path}. Frontend will not load correctly.")

# Catch-all route for SPA
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not found", "path": frontend_path}

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    index_path = os.path.join("static", "index.html")
    return FileResponse(index_path)