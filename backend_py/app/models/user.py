import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func, Uuid
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique primary key identifier (UUIDv4)"
    )
    name = Column(String(255), nullable=False, doc="Full name of user")
    email = Column(String(255), nullable=False, unique=True, index=True, doc="Normalized unique email address")
    password_hash = Column(String(255), nullable=True, doc="Argon2id password hash")
    auth_provider = Column(String(64), nullable=True, default="local", doc="Identity provider (local, google, github)")
    provider_subject = Column(String(255), nullable=True, doc="External OAuth subject / provider ID")
    is_active = Column(Boolean, default=True, nullable=False, doc="Account active state")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<User id={self.id} email={self.email} name={self.name}>"
