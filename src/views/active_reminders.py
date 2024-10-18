import orjson
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession

from .inject_session import inject_session
from src.models.exceptions import InvalidCredentials
from src.models.user import User
from src.models.reminder import Reminder
from ..DTO.reminder_DTO import ReminderDTO


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
        user: User = await User.get_user_by_access_token(
            request.cookies["UserToken"], session
        )

    except (InvalidCredentials, KeyError):
        return web.Response(
            status=401,
            reason="Client is not authorized"
        )

    reminders: tuple[Reminder, ...] = await Reminder.get_active_reminders_of_user(
        user.id, session
    )

    return web.Response(
        body=orjson.dumps(
            [ReminderDTO.from_reminder(reminder) for reminder in reminders]
        )
    )