import orjson
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.user_authentication import authenticate_user
from .inject_session import inject_session
from src.models.exceptions import InvalidCredentials


# post /users/login
@inject_session
async def handle_authentication(request: web.Request, session: AsyncSession) -> web.Response:
    """
    Authenticates user by provided credentials and responds with set-cookie,
    providing access token for future API usage.

    :param request: http request.
    :param session: SQLAlchemy session.
    :return: web response with set-cookie header or error message.
    """
    try:
        request_body: dict =await request.json(loads=orjson.loads)
        username: str = str(request_body["username"]).strip()
        password: str = str(request_body["password"]).strip()

    except (orjson.JSONDecodeError, KeyError, AttributeError):
        return web.Response(status=400, body=orjson.dumps(
            {"reason": "Invalid body format or missing fields from json"}
        ))

    try:
        access_token = await authenticate_user(username, password, session)

    except ValueError:
        return web.Response(status=404, body=orjson.dumps(
            {"reason": "User with provided login does not exists"}
        ))

    except InvalidCredentials:
        return web.Response(status=401, body=orjson.dumps(
            {"reason": "Invalid password provided"}
        ))

    response = web.Response()
    response.set_cookie("UserToken", access_token, httponly=True)

    return response
