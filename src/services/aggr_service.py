import asyncio
from typing import Any

from sqlalchemy import Table, func, select

from src.database import fetch_scalar
from src.models.model import package, release, user
from src.services import package_service


async def get_count(table: Table) -> int | None:
    select_query = select(func.count("*")).select_from(table)
    return await fetch_scalar(select_query)


async def get_count_statistics() -> dict[str, Any]:
    rel = asyncio.create_task(get_count(release))
    usr = asyncio.create_task(get_count(user))
    pck = asyncio.create_task(get_count(package))
    rel, usr, pck = await asyncio.gather(rel, usr, pck)
    return {
        "release_count": rel if rel else 0,
        "user_count": usr if usr else 0,
        "package_count": pck if pck else 0,
    }


async def get_package_details(package_name) -> dict[str, Any]:
    pck = asyncio.create_task(package_service.get_package_by_id(package_name))
    rel = asyncio.create_task(
        package_service.get_latest_release_for_package(package_name)
    )
    maintainers = asyncio.create_task(
        package_service.get_maintainers_by_id(package_name)
    )
    pck, rel, maintainers = await asyncio.gather(pck, rel, maintainers)
    data = {
        "package": pck,
        "latest_release": rel,
        "maintainers": [maintainers] if maintainers else [],
    }
    return data
