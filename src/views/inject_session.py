from functools import wraps
from typing import Callable, Awaitable

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def inject_session(
    handler: Callable[[web.Request, AsyncSession], Awaitable[web.Response]]
) -> Callable[[Request], Awaitable[Response]]:
    """
    Decorator that injects AsyncSession into aiohttp handler.

    :param handler: request handler that needs async session.
    :return: decorated function.
    """
    @wraps(handler)
    async def handle_session(request: web.Request):
        session_maker: async_sessionmaker[AsyncSession] = request.app["session_maker"]
        async with session_maker() as session:
            async with session.begin():
                resp = await handler(request, session)
        return resp
    return handle_session
