from datetime import datetime

from sqlalchemy.exc import (
    DataError, StatementError,
    ProgrammingError, IntegrityError
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.DTO.reminder_created_DTO import ReminderCreatedDTO
from src.models.reminder import Reminder
from src.models.user import User


async def create_reminder(
    user_token: str, session: AsyncSession, /,
    title: str, description: str, color_code: str,
    triggered_at: datetime, is_periodic: bool, trigger_period: int
) -> ReminderCreatedDTO:
    user: User = await User.get_user_by_access_token(
        user_token, session
    )

    try:
        reminder: Reminder | None = await Reminder.create_new_reminder(
            user.id, title, description, color_code, triggered_at,
            is_periodic, trigger_period, session
        )

        if reminder is None:
            raise ValueError("Reminder was not created due to some error")

    except (
        IntegrityError, DataError, StatementError,
        ProgrammingError, ValueError
    ) as e:
        raise ValueError("Incorrect data received") from e

    return ReminderCreatedDTO(True, reminder.id)
