from typing import Any

from sqlalchemy import CursorResult, Insert, Select, Update
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.settings import db_settings

engine = async_engine_from_config(db_settings.config)


async def fetch_one(select_query: Select | Insert | Update) -> dict[str, Any] | None:
    async with engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        result = cursor.first()
        return result._asdict() if result else None


async def fetch_all(select_query: Select | Insert | Update) -> list[dict[str, Any]]:
    async with engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return [r._asdict() for r in cursor.all()]


async def execute(select_query: Insert | Update) -> None:
    async with engine.begin() as conn:
        await conn.execute(select_query)


async def fetch_scalar(select_query: Select) -> Any:
    async with engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return cursor.scalar()
