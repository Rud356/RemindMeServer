import datetime
import secrets
from hashlib import pbkdf2_hmac

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .exceptions import InvalidCredentials
from .initialize_connector import OrmBase


class User(OrmBase):
    """
    Class that represents user in database used by ORM.
    """

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    username: Mapped[str] = mapped_column(unique=True, index=True)
    salt: Mapped[str]
    password: Mapped[str]
    access_token: Mapped[str] = mapped_column(unique=True, index=True)

    @classmethod
    async def register_user(cls, username: str, password: str, session: AsyncSession) -> bool:
        """
        Registers user in database.

        :param username: users name.
        :param password: users password.
        :param session: SQLAlchemy session.
        :return: boolean value representing if use has been saved to database
        """
        salt = secrets.token_urlsafe(64)
        password_hash: str = pbkdf2_hmac(
            'sha256', password.encode('utf-8'),
            salt=salt.encode('utf-8'), iterations=10000
        ).hex()
        access_token: str = await cls.get_unique_access_token(session)

        session.add(
            cls(username=username, password=password_hash, salt=salt, access_token=access_token)
        )
        try:
            await session.commit()
            return True

        except IntegrityError:
            await session.rollback()
            return False

    @classmethod
    async def get_user_by_login_and_password(cls, username: str, password: str, session: AsyncSession) -> "User":
        """
        Fetches user object via provided login and plain password, checks if passwords match,
        and gives back object of user.

        :param username: users login.
        :param password: users plain password.
        :param session: SQLAlchemy session.
        :return: object of class User when password matched one saved in db.
        :raise InvalidCredentials: when password in db and provided by user are mismatching.
        :raise ValueError: if user is not registered.
        """
        query = select(User).where(User.username == username)
        try:
            result: User = (await session.execute(query)).scalars().one()

            password_hash: str = pbkdf2_hmac(
                'sha256', password.encode('utf-8'),
                salt=result.salt.encode('utf-8'), iterations=10000
            ).hex()

            if result.password == password_hash:
                return result

            else:
                raise InvalidCredentials()

        except NoResultFound:
            raise ValueError("No such user registered")

    @classmethod
    async def get_user_by_access_token(cls, access_token: str, session: AsyncSession) -> "User":
        """
        Gets User object from db by access token.

        :param access_token: users access token.
        :param session: SQlAlchemy session.
        :return: object of User class when access_token is in db.
        :raise InvalidCredentials: if there is no such access token in db.
        """
        try:
            query = select(User).where(User.access_token == access_token)
            result: User = (await session.execute(query)).scalars().one()

            return result

        except NoResultFound:
            raise InvalidCredentials()

    @staticmethod
    async def get_unique_access_token(session: AsyncSession) -> str:
        """
        Generates unique access token for usage later.

        :param session: SQLAlchemy session.
        :return: not registered token.
        """
        access_token: str = secrets.token_urlsafe(128)

        token_exists_check = select(
            func.count(User.id)
        ).where(
            User.access_token == access_token
        )
        while await session.scalar(token_exists_check):
            access_token = secrets.token_urlsafe(128)

        return access_token
