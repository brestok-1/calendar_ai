from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from project.config import settings

Base = declarative_base()


def get_async_engine(url: str) -> AsyncEngine:
    return create_async_engine(url=url, echo=True, pool_pre_ping=True)


def get_async_sessionmaker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(bind=engine, class_=AsyncSession)


engine = get_async_engine(
    settings.DATABASE_URL
)
async_session_maker = get_async_sessionmaker(engine)


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        return session