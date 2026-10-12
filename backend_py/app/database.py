from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator
import logging
from .config import settings

logger = logging.getLogger(__name__)

# Determine active database URL with unconfigured safety fallback
db_url = settings.DATABASE_URL
engine_kwargs = {
    "pool_pre_ping": True,
    "future": True
}

if db_url:
    # Supabase cloud PostgreSQL pool settings
    engine_kwargs.update({
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20
    })
else:
    logger.warning("DATABASE_URL is not set. Using in-memory fallback for module imports.")
    db_url = "sqlite:///:memory:"

# Create SQLAlchemy Engine
engine = create_engine(db_url, **engine_kwargs)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

# Declarative Base
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request.
    Ensures sessions are cleanly closed even if exceptions occur.
    """
    if not settings.DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not configured in backend_py/.env. "
            "Please configure your Supabase PostgreSQL connection string."
        )
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session rollback due to exception: {e}")
        raise
    finally:
        db.close()
