from typing import Any

from fastapi import Request

from src.exceptions import AuthRequiredError
from src.settings import cookie_settings
from src.utils import security


def get_auth_cookies_settings(
    user_id: int,
) -> dict[str, Any]:
    base_cookie = {
        "key": cookie_settings.NAME_COOKIES,
        "httponly": cookie_settings.HTTP_ONLY_COOKIES,
        "samesite": cookie_settings.SAMESITE_COOKIES,
        "secure": cookie_settings.SECURE_COOKIES,
    }
    return {
        **base_cookie,
        "value": __get_val(user_id),
    }


def __get_val(user_id: int) -> str:
    hash_val = security.__sign(str(user_id))
    val = "{}:{}".format(security.b64e(str(user_id)), hash_val)
    return val


def get_user_id_via_auth_cookie(request: Request) -> int | None:
    if cookie_settings.NAME_COOKIES not in request.cookies:
        return None

    cookies = request.cookies[cookie_settings.NAME_COOKIES]
    parts = cookies.split(":")
    if len(parts) != 2:
        return None

    user_id = security.b64d(parts[0])
    hash_val = parts[1]
    if not security.__verify_sign(user_id, hash_val):
        raise AuthRequiredError("Hash mismatch, invalid cookie value")

    return try_int(user_id)


def try_int(text) -> int:
    try:
        return int(text)
    except ValueError:
        return 0
