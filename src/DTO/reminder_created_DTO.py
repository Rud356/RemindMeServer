from dataclasses import dataclass


@dataclass
class ReminderCreatedDTO:
    """
    Stores information about newly created reminder.
    """
    is_created: bool
    event_id: int
