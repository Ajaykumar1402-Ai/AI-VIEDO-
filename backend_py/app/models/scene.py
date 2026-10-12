import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func, JSON, UniqueConstraint, Uuid
from sqlalchemy.orm import relationship
from ..database import Base

class Scene(Base):
    __tablename__ = "scenes"

    id = Column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique stable scene identifier (UUIDv4)"
    )
    story_id = Column(
        Uuid,
        ForeignKey("stories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Parent story ID"
    )
    scene_number = Column(Integer, nullable=False, doc="1-indexed sequential position")
    duration_seconds = Column(Integer, nullable=False, doc="Exact scene duration in seconds")
    visual_prompt = Column(Text, nullable=False, doc="High-fidelity visual prompt for LTX-2.5 video engine")
    narration = Column(Text, nullable=True, doc="Voiceover narration text")
    dialogue = Column(JSON, nullable=True, doc="Structured character dialogue list [{character, text, voice_id}]")
    visual_style = Column(String(128), nullable=True, doc="Scene specific visual style override")
    status = Column(String(32), default="pending", nullable=False, doc="Status: pending, audio_generated, video_generated")
    audio_path = Column(String(512), nullable=True, doc="Relative audio artifact reference path")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Constraints & Relationships
    __table_args__ = (
        UniqueConstraint("story_id", "scene_number", name="uq_story_scene_number"),
    )

    story = relationship("Story", back_populates="scenes")

    def __repr__(self):
        return f"<Scene id={self.id} story_id={self.story_id} num={self.scene_number} dur={self.duration_seconds}s>"
