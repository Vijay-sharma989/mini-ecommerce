from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import AsyncSessionlocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionlocal() as session:
        yield session
        