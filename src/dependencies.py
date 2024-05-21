from datetime import datetime

from starlette.requests import Request
from starlette.templating import Jinja2Templates

from src.redis import get_by_key
from src.utils import cookie_auth


def datetime_format(value: datetime, dt_format: str = "%d-%m-%y %H:%M"):
    return value.strftime(dt_format)


def get_templates():
    template = Jinja2Templates(directory="src/templates")
    template.env.filters["datetimeformat"] = datetime_format
    return template


def get_user_id_from_cookie(request: Request):
    return cookie_auth.get_user_id_via_auth_cookie(request)


async def get_package_from_cache(package_name: str):
    key = "package_" + package_name.strip()
    return await get_by_key(key)


async def get_search_from_cache(q: str):
    key = "search_" + q.strip()
    return await get_by_key(key)
