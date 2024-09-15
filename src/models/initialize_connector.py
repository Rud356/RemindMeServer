from sqlalchemy.ext.asyncio import (
    AsyncAttrs, AsyncSession, AsyncEngine,
    create_async_engine, async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase


def create_engine(connection_url: str) -> AsyncEngine:
    return create_async_engine(connection_url)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine)


def initialize_session_maker(connection_url: str) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(
        create_engine(connection_url)
    )


class OrmBase(AsyncAttrs, DeclarativeBase):
    pass
