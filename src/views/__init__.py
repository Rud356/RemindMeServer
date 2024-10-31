from aiohttp import web

from .active_reminders import handle_fetching_active_reminders
from .authenticate_user import handle_authentication
from .create_new_reminder import handle_creating_reminder
from .logout_from_account import handle_logout
from .register_user import handle_registration
from .reminder_specific_actions import (
    handle_fetching_specific_reminder,
    handle_deactivating_specific_reminder,
    handle_updating_specific_reminder
)


def init_application_routes(app: web.Application) -> None:
    app.add_routes(
        [
            web.route(
                "post",
                "/users/register",
                handle_registration
            ),
            web.route(
                "post",
                "/users/login",
                handle_authentication
            ),
            web.route(
                "post",
                "/users/logout",
                handle_logout
            ),
            web.route(
                "get",
                "/reminders/",
                handle_fetching_active_reminders
            ),
            web.route(
                "post",
                "/reminders/",
                handle_creating_reminder
            ),
            web.route(
                "get",
                r"/reminders/{reminderId:\d+}",
                handle_fetching_specific_reminder
            ),
            web.route(
                "delete",
                r"/reminders/{reminderId:\d+}",
                handle_deactivating_specific_reminder
            ),
            web.route(
                "patch",
                r"/reminders/{reminderId:\d+}",
                handle_updating_specific_reminder
            ),
        ]
    )
