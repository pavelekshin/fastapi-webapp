from typing import Any

from sqlalchemy import insert, update
from sqlalchemy.future import select

from src.database import execute, fetch_one
from src.exceptions import InvalidCredentialsError
from src.models.model import user
from src.models.schema import RegisterForm
from src.utils.security import check_password, hash_password


async def create_account(register_form: RegisterForm) -> dict[str, Any] | None:
    insert_query = (
        insert(user)
        .values(
            {
                "name": register_form.name,
                "email": register_form.email,
                "hash_password": hash_password(register_form.password),
            },
        )
        .returning(user)
    )
    return await fetch_one(insert_query)


async def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    user_data = await get_user_by_email(email)
    if not user_data:
        raise InvalidCredentialsError("User not found!")
    if not check_password(password, user_data["hash_password"]):
        raise InvalidCredentialsError("Password not match!")

    return user_data


async def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    select_query = select(user).filter(user.c.id == user_id)
    return await fetch_one(select_query)


async def get_user_by_email(email: str) -> dict[str, Any] | None:
    select_query = select(user).filter(user.c.email == email)
    return await fetch_one(select_query)


async def update_user_login_at(user_id: int) -> None:
    update_query = update(user).where(user.c.id == user_id)
    await execute(update_query)
