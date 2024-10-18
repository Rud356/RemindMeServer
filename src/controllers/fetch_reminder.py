from sqlalchemy.ext.asyncio import AsyncSession

from src.DTO.reminder_DTO import ReminderDTO
from src.models.reminder import Reminder
from src.models.user import User
from .exceptions import ObjectNotFound


async def fetch_specific_reminder(
    user_token: str, reminder_id: int, session: AsyncSession
) -> ReminderDTO:
    """
    Fetches specified reminder by its id if it's related to user
    whose token was provided.

    :param user_token: users token of someone who wants to fetch reminder.
    :param reminder_id: id of reminder to fetch.
    :param session: SQLAlchemy session.
    :return: instance of serializable DTO representing the reminder.

    :raise ObjectNotFound: if reminder was not found in database relating
    to user.
    :raise InvalidCredentials: if users token is not in database.
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

    return ReminderDTO.from_reminder(reminder)
