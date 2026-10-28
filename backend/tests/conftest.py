from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from income_tracker_backend.db import SCHEMA
from income_tracker_backend.store import SqlStore
from suite_backend_core import Base


@pytest.fixture
async def store():
    """A real SqlStore on in-memory SQLite (schema mapped away: SQLite has none)."""
    engine = create_async_engine("sqlite+aiosqlite://").execution_options(
        schema_translate_map={SCHEMA: None}
    )
    async with engine.begin() as conn:
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        await conn.run_sync(Base.metadata.create_all)
    yield SqlStore(async_sessionmaker(engine, expire_on_commit=False))
    await engine.dispose()
