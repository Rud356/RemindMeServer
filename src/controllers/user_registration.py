from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User


async def register_user(username: str, password: str, session: AsyncSession) -> bool:
    """
    Registers new user in database.

    :param username: users login.
    :param password: users password in open form.
    :param session: SQLAlchemy session.
    :return: boolean value that confirms registration
    """
    return await User.register_user(username, password, session)
