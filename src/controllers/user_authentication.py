from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


async def authenticate_user(
    username: str,
    password: str,
    session: AsyncSession
) -> str:
    """
    Authenticates user by checking if provided username
    is associated with provided password
    and returns access token as response.

    :param username: users login.
    :param password: users password in open form.
    :param session: SQLAlchemy session.
    :return: access token if user successfully authenticated.

    :raises ValueError: when user is not registered in database.
    :raises InvalidCredentials: when user did not provide correct password.
    """

    user = await User.get_user_by_login_and_password(
        username, password, session
    )
    return user.access_token
