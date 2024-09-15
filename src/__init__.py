from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from views import init_application_routes


def main(host: str, port: int, session_factory: async_sessionmaker[AsyncSession]):
    app: web.Application = web.Application()
    app["session_maker"] = session_factory
    session_factory()
    init_application_routes(app)

    web.run_app(app, host=host, port=port)
