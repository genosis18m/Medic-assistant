"""
Database configuration for SQLModel with SQLite.
"""
from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
from typing import Generator

DATABASE_URL = "sqlite:///./medical_appointments.db"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
