from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import logging

from ..database import get_db
from ..schemas.auth import HealthDbResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/health", tags=["Health"])

@router.get("", response_model=Dict[str, Any])
@router.get("/", response_model=Dict[str, Any], include_in_schema=False)
def check_health():
    """
    General application health check endpoint.
    Returns basic service uptime status.
    """
    return {
        "status": "healthy",
        "service": "AI Storytelling Platform API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/db", response_model=HealthDbResponse)
def check_db_health(db: Session = Depends(get_db)):
    """
    Lightweight database health check endpoint executing `SELECT version();`
    Reports whether PostgreSQL database is reachable without exposing credentials.
    """
    try:
        result = db.execute(text("SELECT version();")).scalar()
        short_version = result.split()[0] + " " + result.split()[1] if result else "PostgreSQL"
        return HealthDbResponse(
            status="healthy",
            database="PostgreSQL",
            version=short_version,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is unavailable"
        )
