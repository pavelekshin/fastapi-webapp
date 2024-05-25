from typing import Any

from sqlalchemy import select

from src.database import fetch_all, fetch_one
from src.models.model import maintainer, package, release


async def latest_packages(limit: int = 5) -> list[dict[str, Any]]:
    select_query = (
        (select(package).join(release, release.c.package_id == package.c.id))
        .order_by(release.c.create_at.desc())
        .limit(limit)
    )
    return await fetch_all(select_query)


async def get_package_by_id(package_name: str) -> dict[str, Any]:
    select_query = select(package).filter(package.c.id == package_name)
    return await fetch_one(select_query)


async def search_packages_by_id(package_name: str) -> list[dict[str, Any]] | None:
    select_query = select(package).filter(package.c.id.ilike(f"{package_name}%"))
    return await fetch_all(select_query)


async def get_latest_release_for_package(package_name: str) -> dict[str, Any]:
    select_query = (
        select(release).join(package, package.c.id == package_name)
    ).order_by(release.c.create_at.desc())
    return await fetch_one(select_query)


async def get_maintainers_by_id(package_name: str) -> dict[str, Any] | None:
    select_query = select(maintainer).filter(maintainer.c.package_id == package_name)
    return await fetch_one(select_query)
