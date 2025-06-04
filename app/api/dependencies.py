from app.core.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with get_async_db() as db:
        yield db