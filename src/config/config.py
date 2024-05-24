from typing import Any

from dotenv import find_dotenv, load_dotenv
from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings

from src.db.db_folder import get_db_path


class SqlAlchemyConfig:
    """Base config, used for staging SQLAlchemy Engine."""

    __test__ = False

    DATABASE_URL: str = None
    ECHO: bool = False
    ENGINE_OPTIONS: dict[str, Any] = {}

    @property
    def sa_database_uri(self) -> str:
        if self.__class__ is SQLite or PostgreSQL:
            return self.DATABASE_URL
        else:
            raise NotImplementedError("This DB not implemented!")

    @property
    def sa_engine_options(self) -> dict[str, Any]:
        return self.ENGINE_OPTIONS

    @property
    def sa_echo(self) -> bool:
        return self.ECHO

    @property
    def config(self) -> dict[str, Any]:
        cfg = {"sqlalchemy.url": self.sa_database_uri, "sqlalchemy.echo": self.sa_echo}
        for k, v in self.sa_engine_options.items():
            cfg[f"sqlalchemy.{k}"] = v
        return cfg


class PostgreSQL(SqlAlchemyConfig):
    """Uses for PostgresSQL database server."""

    ECHO: bool = False
    ENGINE_OPTIONS: dict[str, Any] = {
        "pool_size": 10,
        "pool_pre_ping": True,
    }

    def __init__(self, url):
        self.DATABASE_URL = url


class SQLite(SqlAlchemyConfig):
    """Uses for SQLite database server."""

    ECHO: bool = True
    ENGINE_OPTIONS: dict[str, Any] = {
        "pool_pre_ping": True,
    }
    DB_NAME = "pypi.sqlite"

    def __init__(self, db_name: str):
        if db_name.strip():
            self.DB_NAME = db_name
        self.DATABASE_URL = f"sqlite+aiosqlite:///{get_db_path(self.DB_NAME)}"


load_dotenv(find_dotenv(".env"))


class CookieConfig(BaseSettings):
    SECURE_COOKIES: bool
    NAME_COOKIES: str
    HTTP_ONLY_COOKIES: bool
    SAMESITE_COOKIES: str
    SECRET_KEY: bytes
    AUTH_SIZE: int


class BaseConfig(BaseSettings):
    REDIS_URL: RedisDsn
    DATABASE_URL: PostgresDsn
    CORS_HEADERS: list[str]
    CORS_ORIGINS: list[str]
    APP_VERSION: str = "1"
