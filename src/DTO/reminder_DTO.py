from datetime import datetime
from dataclasses import dataclass

from src.models.reminder import Reminder


@dataclass
class ReminderDTO:
    """
    DTO for storing and converting Reminder object into JSON.
    """

    id: int
    title: str
    description: str
    color_code: str
    is_active: bool
    is_periodic: bool
    created_at: datetime
    last_edited_at: datetime
    triggered_at: datetime
    trigger_period: int

    @classmethod
    def from_reminder(cls, reminder: Reminder):
        return cls(
            id=reminder.id,
            title=reminder.title,
            description=reminder.description,
            color_code=Reminder.convert_from_int_to_hex(reminder.color_code),
            is_active=reminder.is_active,
            is_periodic=reminder.is_periodic,
            created_at=reminder.created_at,
            last_edited_at=reminder.last_edited_at,
            triggered_at=reminder.triggered_at,
            trigger_period=reminder.trigger_period
        )
