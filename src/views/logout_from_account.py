from aiohttp import web


# post /users/logout
async def handle_logout(request: web.Request) -> web.Response:
    """
    Removes cookie on client side with authentication token if it's present.

    :param request: http request.
    :return: web response with header that removes cookie.
    """

    if request.cookies.get("UserToken"):
        response: web.Response = web.Response()
        response.del_cookie("UserToken")
        return response

    else:
        return web.Response(reason="Not authorized", status=401)
