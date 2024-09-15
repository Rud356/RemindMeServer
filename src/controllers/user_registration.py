from sqlalchemy.ext.asyncio import AsyncSession


async def register_user(username: str, password: str, session: AsyncSession) -> bool:
    """
    Registers new user in database.
    :param username: users login.
    :param password: users password in open form.

    :return: boolean value that confirms registration
    """
    return True
