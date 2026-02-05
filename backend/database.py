"""
Database configuration for SQLModel with PostgreSQL.
Supports both sync and async operations.
"""
import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment, fallback to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medical_appointments.db")

# Convert postgres:// to postgresql:// if needed (Heroku/Railway compatibility)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create sync engine
sync_engine = create_engine(DATABASE_URL, echo=False)

# Create async engine if using PostgreSQL
ASYNC_DATABASE_URL = None
async_engine = None

if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )


def create_db_and_tables() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(sync_engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = Session(sync_engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async transactional scope for PostgreSQL operations."""
    if async_engine is None:
        raise RuntimeError("Async database not configured. Use PostgreSQL for async support.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
