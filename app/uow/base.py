import asyncio
from sqlalchemy.ext.asyncio import AsyncSession


class BaseUnitOfWork:
    def __init__(self, session_factory):
        self._session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        if callable(self._session_factory):
            maybe_session = self._session_factory()
            if asyncio.iscoroutine(maybe_session):
                self.session = await maybe_session
            else:
                self.session = maybe_session
        else:
            raise TypeError("session_factory має бути callable")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            if self.session:
                await self.session.close()

    async def commit(self):
        if self.session:
            await self.session.commit()

    async def rollback(self):
        if self.session:
            await self.session.rollback()
