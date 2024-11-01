from datetime import datetime
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.exceptions import ObjectNotFound
from src.models.reminder import Reminder
from src.models.user import User


async def update_specific_reminder(
    user_token: str, reminder_id: int, session: AsyncSession, *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    color_code: Optional[str] = None,
    triggered_at: Optional[datetime] = None,
    is_periodic: Optional[bool] = None,
    trigger_period: Optional[int] = None
) -> list[str]:
    """
    Updates fields of specific event that is created by user,
    whose token is provided in request.

    :param user_token: users token of someone who wants to update reminder.
    :param reminder_id: id of reminder to update.
    :param session: SQLAlchemy session.
    :param title: new title.
    :param description: new description.
    :param color_code: HEX color code in string format.
    :param triggered_at: when will event be triggered first time.
    :param is_periodic: will event be triggered again in some period.
    :param trigger_period: how many days should pass before
    event is triggered again.
    :param _: stores all invalid keys.
    :return: list of updated fields.

    :raise ProgrammingError: if case one of parameters received
    invalid data that has wrong type.
    :raise ValueError: if no fields to update.
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

    fields: dict[str, Any] = {}

    if title is not None:
        fields["title"] = title

    if description is not None:
        fields["description"] = description

    if color_code is not None:
        fields["color_code"] = color_code

    if triggered_at is not None:
        fields["triggered_at"] = triggered_at

    if trigger_period is not None:
        fields["trigger_period"] = trigger_period

    if is_periodic is not None:
        fields["is_periodic"] = is_periodic

    if len(fields) == 0:
        raise ValueError("Fields not updated")

    return await reminder.update_reminder(session, **fields)
