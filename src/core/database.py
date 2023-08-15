from dependency_injector.providers import Singleton
from contextlib import asynccontextmanager
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
logger = logging.getLogger(__name__)


class Database(Singleton):
    def __init__(self, db_url: str) -> None:
        super().__init__()

        self._engine = create_async_engine(db_url, echo=True, future=True)
        self._session_factory = async_sessionmaker(self._engine, autoflush=False, expire_on_commit=False)

    async def create_database(self) -> None:
        async with self._engine.begin() as connect:
            await connect.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                logger.exception("Session rollback because of exception")
                await session.rollback()
                raise
            finally:
                await session.close()
