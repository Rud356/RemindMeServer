import re

import orjson
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.user_registration import register_user
from .inject_session import inject_session

USERNAME_REGEX = re.compile(r"^[A-z0-9_]{8,}")
USER_PASSWORD_REGEX = re.compile(r"^[A-z0-9_+\-=]{8,}")


# post /users/register
@inject_session
async def handle_registration(
    request: web.Request, session: AsyncSession
) -> web.Response:
    """
    Registers user in system.

    :param request: http request.
    :param session: SQLAlchemy session.
    :return: web response with reason or indication.
    """
    try:
        request_body: dict = await request.json(loads=orjson.loads)
        username: str = str(request_body["username"]).strip()

        if USERNAME_REGEX.fullmatch(username) is None:
            return web.Response(
                status=400,
                body=orjson.dumps(
                    {
                        "reason":
                            "Incorrect incoming body, expected ascii "
                            "sequence of 8 symbols for username"
                    }
                )
            )

        password: str = str(request_body["password"]).strip()

        if USER_PASSWORD_REGEX.fullmatch(password) is None:
            return web.Response(
                status=400,
                body=orjson.dumps(
                    {
                        "reason":
                            "Incorrect incoming body, expected at least "
                            "8 ascii characters as password"
                    }
                )
            )

        successful_registration = await register_user(
            username, password, session
        )

    except (orjson.JSONDecodeError, KeyError, AttributeError):
        return web.Response(
            status=400,
            body=orjson.dumps(
                {
                    "reason": "Incorrect incoming body, expected json"
                }
            )
        )

    if successful_registration:
        return web.Response(
            body=orjson.dumps(
                {
                    "registered": successful_registration
                }
            )
        )

    else:
        return web.Response(
            status=409,
            body=orjson.dumps(
                {
                    "reason": "User is already registered in database "
                              "with such login",
                    "registered": successful_registration
                }
            )
        )
