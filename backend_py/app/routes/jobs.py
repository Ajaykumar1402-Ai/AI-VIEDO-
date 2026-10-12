from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from ..database import get_db
from ..models.user import User
from ..models.job import GenerationJob
from ..models.project import Project
from ..schemas.story import JobResponse
from ..security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Poll the status of an asynchronous generation job.
    Ensures user owns the parent project.
    """
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check project ownership
    project = db.query(Project).filter(Project.id == job.project_id).first()
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden - You do not own this job"
        )

    return JobResponse.model_validate(job)
