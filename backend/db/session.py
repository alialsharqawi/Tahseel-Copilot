from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import get_database_url


@lru_cache(maxsize=4)
def get_engine(database_url: str) -> Engine:
    """Create and cache a SQLAlchemy engine for the given database URL."""
    return create_engine(database_url, pool_pre_ping=True)


def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    """Return a session factory bound to the configured database URL."""
    resolved_url = database_url or get_database_url()
    engine = get_engine(resolved_url)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Yield a request-scoped database session with rollback on error."""
    session = get_session_factory()()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
