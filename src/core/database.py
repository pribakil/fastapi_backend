from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

# Async Postgres database connection url
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:admin2025@localhost:5432/test_db1"
    )

# Async engine
engine = create_async_engine(DATABASE_URL, echo = False, future = True)

# Session factory
AsyncSessionLocal = sessionmaker(
    bind = engine,
    expire_on_commit = False, # we use sessionmaker instead of the AsyncSession class
    class_ = AsyncSession,
    )

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session