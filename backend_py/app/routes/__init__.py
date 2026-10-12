from .auth import router as auth_router
from .health import router as health_router
from .projects import router as projects_router
from .jobs import router as jobs_router

__all__ = ["auth_router", "health_router", "projects_router", "jobs_router"]
