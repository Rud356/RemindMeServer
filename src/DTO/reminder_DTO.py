from datetime import datetime
from dataclasses import dataclass


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
