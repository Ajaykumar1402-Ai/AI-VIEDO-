import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func, Uuid
from sqlalchemy.orm import relationship
from ..database import Base

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique job identifier (UUIDv4)"
    )
    project_id = Column(
        Uuid,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Associated project ID"
    )
    story_id = Column(
        Uuid,
        ForeignKey("stories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Associated story ID"
    )
    job_type = Column(
        String(64),
        nullable=False,
        doc="Job type: story_generation, tts_generation, video_generation"
    )
    status = Column(
        String(32),
        default="pending",
        nullable=False,
        index=True,
        doc="Job status: pending, processing, completed, failed"
    )
    progress = Column(Integer, default=0, nullable=False, doc="Job progress percentage (0-100)")
    error_message = Column(Text, nullable=True, doc="Safe error message if job failed")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="jobs")
    story = relationship("Story", back_populates="jobs")

    def __repr__(self):
        return f"<GenerationJob id={self.id} type={self.job_type} status={self.status} progress={self.progress}%>"
