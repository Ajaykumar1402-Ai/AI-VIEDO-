import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func, Uuid
from sqlalchemy.orm import relationship
from ..database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique project identifier (UUIDv4)"
    )
    user_id = Column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Owner user ID"
    )
    title = Column(String(255), nullable=False, doc="Project title")
    description = Column(Text, nullable=True, doc="Optional project summary or concept")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="projects")
    stories = relationship("Story", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("GenerationJob", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project id={self.id} title='{self.title}' user_id={self.user_id}>"
