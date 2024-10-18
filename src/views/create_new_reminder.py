from datetime import datetime
from typing import Any

import orjson
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession

from src.DTO.reminder_created_DTO import ReminderCreatedDTO
from src.controllers.create_reminder import create_reminder
from src.models.exceptions import InvalidCredentials
from .inject_session import inject_session


# post /reminders/
@inject_session
async def handle_fetching_active_reminders(
    request: web.Request, session: AsyncSession
) -> web.Response:
    """

    :param request:
    :param session:
    :return:
    """

    try:
        user_token: str = request.cookies["UserToken"]

    except KeyError:
        return web.Response(
            status=401,
            reason="Client is not authorized"
        )

    try:
        body: dict[str, Any] = await request.json()
        new_event_data: dict[str, Any] = {
            "title": body["title"].strip(),
            "description": body["description"].strip(),
            "color_code": body["color_code"].strip(),
            "triggered_at": datetime.fromisoformat(body["triggered_at"]),
            "is_periodic": body["is_periodic"],
            "trigger_period": int(body["trigger_period"])
        }

        if not isinstance(new_event_data["is_periodic"], bool):
            raise TypeError("Invalid type for is_periodic variable")

        result: ReminderCreatedDTO = await create_reminder(
            user_token, session, **new_event_data
        )

        return web.Response(
            body=orjson.dumps(result)
        )

    except (TypeError, ValueError, AttributeError):
        return web.Response(
            status=400,
            reason="Invalid request body"
        )

    except InvalidCredentials:
        return web.Response(
            status=401,
            reason="Client is not authorized"
        )
