from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import settings
from .routes.auth import router as auth_router
from .routes.health import router as health_router
from .routes.projects import router as projects_router
from .routes.jobs import router as jobs_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("storytelling_app")

app = FastAPI(
    title="AI Storytelling Platform API",
    description="Production PostgreSQL-backed FastAPI service for Gemini AI Story Generation and Self-Hosted TTS",
    version="1.0.0"
)

# Configure CORS for Frontend
origins = [
    settings.FRONTEND_ORIGIN,
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(jobs_router)

@app.get("/")
def root():
    return {
        "service": "AI Storytelling Platform API",
        "status": "online",
        "docs": "/docs",
        "health": "/api/health/db"
    }
