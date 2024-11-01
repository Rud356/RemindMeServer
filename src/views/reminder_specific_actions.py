from datetime import datetime
from typing import Any

import orjson
from aiohttp import web
from sqlalchemy.exc import DataError, StatementError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from src.DTO.reminder_DTO import ReminderDTO
from src.controllers.deactivate_reminder import deactivate_specific_reminder
from src.controllers.exceptions import ObjectNotFound
from src.controllers.fetch_reminder import fetch_specific_reminder
from src.controllers.update_reminder import update_specific_reminder
from src.models.exceptions import InvalidCredentials
from .inject_session import inject_session


# get /reminders/{reminderId:\d+}
@inject_session
async def handle_fetching_specific_reminder(
    request: web.Request, session: AsyncSession
) -> web.Response:
    """
    Fetches specified users reminder.

    :param request: http request.
    :param session: SQLAlchemy session.
    :return: web response with reminder or error message.
    """

    try:
        user_token: str = request.cookies["UserToken"]

    except KeyError:
        return web.Response(
            status=401,
            reason="Client is not authorized"
        )

    try:
        # Fetching reminder by url variable
        reminder: ReminderDTO = await fetch_specific_reminder(
            user_token, int(request.match_info["reminderId"]), session
        )

        return web.Response(
            body=orjson.dumps(reminder)
        )

    except (DataError, ValueError, KeyError):
        return web.Response(
            status=400,
            reason="Provided parameter in request is invalid"
        )

    except InvalidCredentials:
        return web.Response(
            status=401,
            reason="Client is not authorized"
        )

    except (AttributeError, ObjectNotFound):
        return web.Response(
            status=404,
            body=orjson.dumps({
                "reason":
                    "Provided ID in URL parameter is not found for that user"
            })
        )


# delete /reminders/{reminderId:\d+}
@inject_session
async def handle_deactivating_specific_reminder(
    request: web.Request, session: AsyncSession
) -> web.Response:
    """
    Deletes specified users reminder.

    :param request: http request.
    :param session: SQLAlchemy session.
    :return: web response with confirmation that
    reminder is deleted or error message.
    """

    try:
        user_token: str = request.cookies["UserToken"]

    except KeyError:
        return web.Response(
            status=401,
            reason="Client is not authorized"
        )

    try:
        body: dict[str, int | bool] = await deactivate_specific_reminder(
            user_token, int(request.match_info["reminderId"]), session
        )

        return web.Response(
            body=orjson.dumps(body)
        )

    except (DataError, ValueError, KeyError):
        return web.Response(
            status=400,
            reason="Provided parameters in request are invalid"
        )

    except InvalidCredentials:
        return web.Response(
            status=401,
            reason="Client is not authorized"
        )

    except (AttributeError, ObjectNotFound):
        return web.Response(
            status=404,
            body={
                "reason":
                    "Provided ID in URL parameter is not found for that user"
            }
        )


# patch /reminders/{reminderId:\d+}
@inject_session
async def handle_updating_specific_reminder(
    request: web.Request, session: AsyncSession
) -> web.Response:
    """
    Fetches specified users reminder.

    :param request: http request.
    :param session: SQLAlchemy session.
    :return: web response with reminder or error message.
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

        if "triggered_at" in body:
            try:
                body["triggered_at"] = datetime.fromisoformat(
                    body["triggered_at"]
                )

            except TypeError as e:
                raise ValueError(
                    f"Invalid triggered_at field type "
                    f"(got {type(body['triggered_at'])}"
                ) from e

        updated_fields: list[str] = await update_specific_reminder(
            user_token, int(request.match_info["reminderId"]), session,
            **body
        )

        return web.Response(
            body=orjson.dumps(updated_fields)
        )

    except (DataError, StatementError, ProgrammingError, AttributeError, TypeError, ValueError):
        return web.Response(
            status=400,
            reason="Invalid request body or URL parameter"
        )

    except InvalidCredentials:
        return web.Response(
            status=401,
            reason="Client is not authorized"
        )

    except (KeyError, ObjectNotFound) as e:
        return web.Response(
            status=404,
            body=orjson.dumps(
                {
                    "reason":
                        "Provided ID in URL parameter is not found for that user"
                }
            )
        )
