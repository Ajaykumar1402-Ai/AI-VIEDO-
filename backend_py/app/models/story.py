import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, JSON, Uuid
from sqlalchemy.orm import relationship
from ..database import Base

class Story(Base):
    __tablename__ = "stories"

    id = Column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique story identifier (UUIDv4)"
    )
    project_id = Column(
        Uuid,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Associated project ID"
    )
    version = Column(Integer, default=1, nullable=False, doc="Story revision version")
    title = Column(String(255), nullable=False, doc="Generated story title")
    language = Column(String(32), default="en", nullable=False, doc="Language code (e.g., en, es, fr)")
    genre = Column(String(64), nullable=False, doc="Genre (e.g. science_fiction, fantasy, drama)")
    visual_style = Column(String(128), nullable=False, doc="Visual aesthetic (e.g., cinematic realism)")
    target_duration_seconds = Column(Integer, nullable=False, doc="Target overall duration in seconds")
    story_metadata = Column(JSON, nullable=True, doc="Arbitrary story metadata, character sheets, synopsis")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="stories")
    scenes = relationship("Scene", back_populates="story", cascade="all, delete-orphan", order_by="Scene.scene_number")
    jobs = relationship("GenerationJob", back_populates="story")

    def __repr__(self):
        return f"<Story id={self.id} title='{self.title}' project_id={self.project_id}>"
