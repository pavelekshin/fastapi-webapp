from typing import Any

from sqlalchemy import Table, func, select

from src.database import fetch_scalar
from src.models.model import package, release, user
from src.services import package_service


async def get_count(table: Table) -> int | None:
    select_query = select(func.count(table.c.id))
    return await fetch_scalar(select_query)


async def get_count_statistics() -> dict[str, Any]:
    return {
        "release_count": await get_count(release),
        "user_count": await get_count(user),
        "package_count": await get_count(package),
        "packages": await package_service.latest_packages(limit=7),
    }


async def get_package_details(package_name) -> dict[str, Any]:
    data = {
        "package": await package_service.get_package_by_id(package_name),
        "latest_release": await package_service.get_latest_release_for_package(
            package_name,
        ),
        "maintainers": [],
    }

    if maintainers := await package_service.get_maintainers_by_id(package_name):
        data["maintainers"].append(maintainers)

    return data
