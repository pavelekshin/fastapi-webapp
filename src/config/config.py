from typing import Any

from dotenv import find_dotenv, load_dotenv
from pydantic import RedisDsn, PostgresDsn
from pydantic_settings import BaseSettings

from src.db.db_folder import get_db_path


class Config:
    """Base config, uses staging SQLAlchemy Engine."""

    __test__ = False

    DATABASE_URL: str = None
    ECHO: bool = False
    DB_NAME: str = None
    ENGINE_OPTIONS: dict[str, Any] = {}

    @property
    def sa_database_uri(self) -> str:
        if self.__class__ is SQLite:
            return f"sqlite+aiosqlite:///{get_db_path(self.DB_NAME)}"
        elif self.__class__ is PostgreSQL:
            return self.DATABASE_URL
        else:
            raise NotImplementedError("This DB not implemented!")

    @property
    def sa_engine_options(self) -> dict[str, Any]:
        return self.ENGINE_OPTIONS

    @property
    def sa_echo(self) -> bool:
        return self.ECHO

    def _db_filename(self) -> str:
        return get_db_path(self.DB_NAME)

    @property
    def config(self) -> dict[str, Any]:
        cfg = {"sqlalchemy.url": self.sa_database_uri, "sqlalchemy.echo": self.sa_echo}
        for k, v in self.sa_engine_options.items():
            cfg[f"sqlalchemy.{k}"] = v
        return cfg


class PostgreSQL(Config):
    """Uses for PostgresSQL database server."""

    ECHO: bool = False
    ENGINE_OPTIONS: dict[str, Any] = {
        "pool_size": 10,
        "pool_pre_ping": True,
    }

    def __init__(self, url):
        self.DATABASE_URL = url


class SQLite(Config):
    """Uses for SQLite database server."""

    ECHO: bool = True
    DB_NAME: str = "pypi.sqlite"
    ENGINE_OPTIONS: dict[str, Any] = {
        "pool_pre_ping": True,
    }

    def __init__(self, db_name):
        self.DB_NAME = db_name


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
