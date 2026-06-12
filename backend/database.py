"""
Database engine, session factory, and initialization helpers.

Uses SQLAlchemy with SQLite. The `get_db` generator is designed to be
used as a FastAPI dependency so every request gets its own session that
is automatically closed after the response is sent.
"""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.config import settings

# ── Engine & session factory ────────────────────────────────────────────

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Declarative base ───────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Base class for all ORM models."""


# ── Dependency ──────────────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session.

    The session is committed on success and rolled back on error,
    then always closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Initialisation ──────────────────────────────────────────────────────

def init_db() -> None:
    """Create all tables and ensure the ``data/`` directory exists.

    Safe to call multiple times – SQLAlchemy's ``create_all`` is a no-op
    for tables that already exist.
    """
    # Ensure the data directory exists for the SQLite file.
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    data_dir = Path(db_path).parent
    data_dir.mkdir(parents=True, exist_ok=True)

    # Import models so they are registered on Base.metadata.
    import backend.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
