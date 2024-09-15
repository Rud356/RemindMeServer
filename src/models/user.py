import datetime
import secrets

from hashlib import pbkdf2_hmac

from sqlalchemy import func, select, and_
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .initialize_connector import OrmBase
from .exceptions import InvalidCredentials


class User(OrmBase):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = func.now()
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
        :param session:
        :return: boolean value representing if use has been saved to database
        """
        salt = secrets.token_urlsafe(64)
        password_hash: str = pbkdf2_hmac('sha256', password.encode('utf-8'), salt=salt, iterations=10000).hex()
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
        query = select(User).where(User.username == username)
        try:
            result: User = (await session.execute(query)).scalars().first()

            password_hash: str = pbkdf2_hmac(
                'sha256', password.encode('utf-8'),
                salt=result.salt, iterations=10000
            ).hex()

            if result.password == password_hash:
                return result

            else:
                raise InvalidCredentials()

        except NoResultFound:
            raise ValueError("No such user registered")

    @classmethod
    async def get_user_by_access_token(cls, access_token: str, session: AsyncSession) -> "User":
        try:
            query = select(User).where(User.access_token == access_token)
            result: User = (await session.execute(query)).scalars().first()

            return result

        except NoResultFound:
            raise InvalidCredentials()

    @staticmethod
    async def get_unique_access_token(session: AsyncSession) -> str:
        access_token: str = secrets.token_urlsafe(128)

        token_exists_check = select(
            func.count(User)
        ).where(
            User.access_token == access_token
        )
        while await session.scalar(token_exists_check):
            access_token: str = secrets.token_urlsafe(128)

        return access_token
