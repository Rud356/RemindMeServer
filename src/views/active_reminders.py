import orjson
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession

from src.DTO.reminder_DTO import ReminderDTO
from src.models.exceptions import InvalidCredentials
from .inject_session import inject_session
from ..controllers.fetch_all_reminders import fetch_all_reminders


# get /reminders/
@inject_session
async def handle_fetching_active_reminders(
    request: web.Request, session: AsyncSession
) -> web.Response:
    """
    Fetches all users active reminders.

    :param request: http request.
    :param session: SQLAlchemy session.
    :return: web response with all active reminders or error message.
    """

    try:
        reminders: list[ReminderDTO] = await fetch_all_reminders(
            request.cookies["UserToken"],
            session
        )

        return web.Response(body=orjson.dumps(reminders))

    except (InvalidCredentials, KeyError):
        return web.Response(
            status=401,
            reason="Client is not authorized"
        )

