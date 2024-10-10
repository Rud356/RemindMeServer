from aiohttp import web

from .register_user import handle_registration

def init_application_routes(app: web.Application) -> None:
    app.add_routes(
        [
            web.route("post", "/users/register", handle_registration)
        ]
    )
