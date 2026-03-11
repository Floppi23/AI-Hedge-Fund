"""Initialize database tables directly (for SQLite dev). Use Alembic for PostgreSQL production."""

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from app.config import Settings
from app.db.base import Base
from app.models import *  # noqa: F401, F403


async def create_tables():
    settings = Settings()
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print(f"Tables created in {settings.database_url}")


if __name__ == "__main__":
    asyncio.run(create_tables())
