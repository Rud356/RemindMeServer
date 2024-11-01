from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.reminder import Reminder
from src.models.user import User
from .exceptions import ObjectNotFound


async def deactivate_specific_reminder(
    user_token: str, reminder_id: int, session: AsyncSession
) -> dict[str, int | bool]:
    """
    Deactivates specified reminder by its id if it is created by user who
    makes request, resulting in being not listed in future when requesting
    all reminders.

    :param user_token: users token of someone who wants to deactivate reminder.
    :param reminder_id: id of reminder to deactivate.
    :param session: SQLAlchemy session.
    :return: dict with prepared view that can be serialized into response.

    :raise ObjectNotFound: if reminder was not found in database relating
    to user.
    :raise InvalidCredentials: if users token is not in database.
    :raise HTTPInternalServerError: if objects were found, but
    deactivation failed.
    """
    user: User = await User.get_user_by_access_token(
        user_token, session
    )

    reminder: Reminder | None = await Reminder.get_reminder_by_id(
        user.id, reminder_id, session
    )

    if reminder is None:
        raise ObjectNotFound(
            f"Reminder with id {reminder_id} was not found "
            f"for user with id {user.id}"
        )

    event_id: int = reminder.id
    is_deactivated: bool = await reminder.deactivate_reminder(session)
    if not is_deactivated:
        # Unknown reason, need to check logs
        raise web.HTTPInternalServerError()

    return {
        "deleted_event_id": event_id,
        "has_been_deactivated": is_deactivated
    }
