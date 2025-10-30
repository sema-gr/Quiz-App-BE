import os
import sys
import pytest
import asyncio
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import Base

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    print("TEST_DATABASE_URL не встановлено! Скасування тестів.")
    sys.exit(1)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    if "test" not in TEST_DATABASE_URL:
        print(
            f"TEST_DATABASE_URL ({TEST_DATABASE_URL}) не схожий на тестову БД! Скасування."
        )
        sys.exit(1)

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(db_engine):
    async with db_engine.connect() as connection:
        trans = await connection.begin()
        TestSessionLocal = async_sessionmaker(
            bind=connection, expire_on_commit=False, class_=AsyncSession
        )
        session = TestSessionLocal()

        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
