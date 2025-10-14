import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.settings import settings
from app.core.database import Base

TEST_DATABASE_URL = settings.database_url

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture
async def async_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        yield session
        await session.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
