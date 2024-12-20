from sqlalchemy.ext.asyncio import (
    AsyncAttrs, AsyncSession, AsyncEngine,
    create_async_engine, async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase


def create_engine(connection_url: str) -> AsyncEngine:
    """
    Creates db engine.

    :param connection_url: string with initialization parameters for engine.
    :return: engine instance.
    """
    return create_async_engine(connection_url)


def create_session_factory(
    engine: AsyncEngine
) -> async_sessionmaker[AsyncSession]:
    """
    Creates session factory from session.

    :param engine: provided engine.
    :return: async_sessionmaker factory.
    """
    return async_sessionmaker(engine)


def initialize_session_maker(
    connection_url: str
) -> async_sessionmaker[AsyncSession]:
    """
    Combines engine creation and session factory creation.

    :param connection_url: string with initialization parameters for engine.
    :return: async_sessionmaker factory.
    """
    return create_session_factory(
        create_engine(connection_url)
    )


async def reinitialize_db(engine: AsyncEngine) -> None:
    user_module = __import__(  # noqa: F841
        "src.models.user"
    )
    reminder_module = __import__(  # noqa: F841
        "src.models.reminder"
    )

    async with engine.begin() as conn:
        await conn.run_sync(OrmBase.metadata.drop_all)
        await conn.run_sync(OrmBase.metadata.create_all)


class OrmBase(AsyncAttrs, DeclarativeBase):
    """
    Base class for ORM models.
    """
    pass
