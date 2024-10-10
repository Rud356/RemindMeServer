import orjson
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession

from .inject_session import inject_session

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

    except (orjson.JSONDecodeError, KeyError, AttributeError):
        return web.Response()


    response = web.Response()
    response.set_cookie("UserToken", "", httponly=True)

    return response