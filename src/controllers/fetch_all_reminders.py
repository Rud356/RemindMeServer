from sqlalchemy.ext.asyncio import AsyncSession
from src.DTO.reminder_DTO import ReminderDTO
from src.models.reminder import Reminder
from src.models.user import User


async def fetch_all_reminders(
    user_token: str, session: AsyncSession
) -> list[ReminderDTO]:
    user: User = await User.get_user_by_access_token(
        user_token, session
    )

    reminders: tuple[Reminder, ...] = await Reminder.get_active_reminders_of_user(
        user.id, session
    )
    return [ReminderDTO.from_reminder(reminder) for reminder in reminders]