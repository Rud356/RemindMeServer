from __future__ import annotations

import datetime

from sqlalchemy import (
    and_, select, func,
    String, CheckConstraint, ForeignKey, DateTime
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .initialize_connector import OrmBase


class Reminder(OrmBase):
    """
    Class that represents reminder in database used by ORM.
    """

    __tablename__ = "reminder"

    id: Mapped[int] = mapped_column(primary_key=True)
    authored_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id")
    )
    # Notification title
    title: Mapped[str] = mapped_column(
        String(65),
        CheckConstraint("length(title) > 0")
    )
    # Notification description
    description: Mapped[str] = mapped_column(
        String(240)
    )
    # Color code for reminder in app
    color_code: Mapped[int] = mapped_column(
        CheckConstraint(
            "color_code BETWEEN 0 AND (256*256*256 - 1)"
        )
    )
    # Is reminder active and sends notifications
    is_active: Mapped[bool] = mapped_column(default=True)
    # Is reminder repeating itself on intervals
    is_periodic: Mapped[bool]
    # When reminder was created
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    # When was the last edit (used for syncing and overriding old reminders
    last_edited_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    # When will event be first triggered at
    triggered_at: Mapped[datetime.datetime]
    # How many days before the event will be triggered again
    trigger_period: Mapped[int] = mapped_column(
        CheckConstraint(
            "trigger_period >= 0"
        )
    )

    async def update_reminder(
        self, session: AsyncSession, **fields
    ) -> list[str]:
        """
        Modifies allowed fields of specific reminder.

        :param session: SQLAlchemy session.
        :param fields: fields to update. Allowed fields are:
        title, description, color_code,
        is_periodic, triggered_at, trigger_period.
        :return: list of fields names that were modified.
        """

        MODIFIABLE_FIELDS: frozenset[str] = frozenset({
            'title', 'description',
            'color_code', 'is_periodic',
            'triggered_at', 'trigger_period',
        })

        fields_to_modify = set(fields.keys()) & MODIFIABLE_FIELDS
        modified_fields = []

        try:
            if 'color_code' in fields_to_modify:
                fields_to_modify.remove('color_code')
                modified_fields.append('color_code')
                self.color_code: int = self.convert_from_hex_to_int_color(
                    fields['color_code']
                )

            for key in fields_to_modify:
                # dynamically update all fields
                setattr(self, key, fields[key])
                modified_fields.append(key)

            self.last_edited_at = datetime.datetime.now(datetime.UTC)
            # Try commiting changes to database to check if values are ok
            await session.commit()
            return modified_fields

        except IntegrityError:
            await session.rollback()
            return []

    async def deactivate_reminder(self, session: AsyncSession) -> bool:
        try:
            self.is_active: bool = False
            self.last_edited_at = datetime.datetime.now(datetime.UTC)
            await session.commit()
            return True

        except IntegrityError:
            await session.rollback()
            return False

    @classmethod
    async def create_new_reminder(
        cls, user_id: int, title: str, description: str,
        color_code: str, triggered_at: datetime.datetime,
        is_periodic: bool, trigger_period: int, session: AsyncSession
    ) -> Reminder | None:
        reminder = cls(
            authored_by_user_id=user_id,
            title=title,
            description=description,
            color_code=cls.convert_from_hex_to_int_color(color_code),
            triggered_at=triggered_at,
            is_periodic=is_periodic,
            trigger_period=trigger_period
        )

        async with session.begin_nested() as tr:
            session.add(reminder)
            try:
                await tr.commit()

            except IntegrityError:
                await tr.rollback()
                return None

        return reminder

    @classmethod
    async def get_reminder_by_id(
        cls, user_id: int, reminder_id: int, session: AsyncSession
    ) -> Reminder | None:
        """
        Fetches reminder by its ID and ID of user who authored reminder.

        :param user_id: user who requests reminder by ID.
        :param reminder_id: ID of reminder to fetch.
        :param session: SQLAlchemy session.
        :return: instance of Reminder or None in case there's
        no such Reminder for that user.
        """
        query = select(cls).where(
            and_(
                cls.authored_by_user_id == user_id,
                cls.id == reminder_id
            )
        )
        result: Reminder | None = (await session.execute(query)).scalar()
        return result

    @classmethod
    async def get_active_reminders_of_user(
        cls, user_id: int, session: AsyncSession
    ) -> tuple[Reminder, ...]:
        """
        Fetches all active reminders that belong to specified user.

        :param user_id: user whose reminders need to be fetched.
        :param session: SQLAlchemy session.
        :return: tuple of Reminder objects.
        """
        query = select(cls).where(
            and_(
                cls.authored_by_user_id == user_id,
                cls.is_active.is_(True)
            )
        )

        return tuple((await session.execute(query)).scalars().all())

    @classmethod
    async def get_deactivated_reminders_of_user(
        cls, user_id: int, session: AsyncSession
    ) -> tuple[Reminder, ...]:
        """
        Fetches all deactivated reminders that belong to specified user.
        :param user_id: user whose reminders need to be fetched.
        :param session: SQLAlchemy session.
        :return: tuple of Reminder objects.
        """
        query = select(cls).where(
            and_(
                cls.authored_by_user_id == user_id,
                cls.is_active.is_(False)
            )
        )

        return tuple((await session.execute(query)).scalars().all())

    @staticmethod
    def convert_from_hex_to_int_color(hex_color: str) -> int:
        """
        Helper method that converts hex string into integer value,
        and checks boundaries.

        :param hex_color: input string of HEX color representation
        (RRGGBB format).
        :return: converted integer value.
        :raises ValueError: if string is invalid value in base 16
        or out of possible HEX color range.
        """
        if (value := int(hex_color, 16)) not in range(0, 256**3):
            raise ValueError("Invalid boundaries for HEX color")

        return value

    @staticmethod
    def convert_from_int_to_hex(color: int) -> str:
        """
        Converts int representation of color into HEX string
        with leading zeros.

        :param color: integer representing the color in RRGGBB format.
        :return:
        """
        return f'{color:x}'.zfill(6).upper()
