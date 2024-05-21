from typing import Any

from dotenv import find_dotenv, load_dotenv
from pydantic import RedisDsn
from pydantic_settings import BaseSettings

from src.db.db_folder import get_db_path


class Config:
    """Base config, uses staging SQLAlchemy Engine."""

    __test__ = False

    ECHO: bool = False
    DB_SERVER: str = None
    DB_USER: str = None
    DB_PASSWORD: str = None
    DB_NAME: str = None
    PORT: int = 5432
    ENGINE_OPTIONS: dict[str, Any] = {}

    def __init__(self, host=None, dbname=None, username=None, password=None):
        if host:
            self.DB_SERVER = host
        if dbname:
            self.DB_NAME = dbname
        if username:
            self.DB_USER = username
        if password:
            self.DB_PASSWORD = password

    @property
    def sa_database_uri(self) -> str:
        if self.__class__ is SQLite:
            return f"sqlite+aiosqlite:///{get_db_path(self.DB_NAME)}"
        elif self.__class__ is PostgresSQL:
            return (
                f"postgresql+asyncpg://"
                f"{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_SERVER}:{self.PORT}/{self.DB_NAME}"
            )
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


class PostgresSQL(Config):
    """Uses for PostgresSQL database server."""

    DB_SERVER: str = "localhost"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "postgres"
    PORT: int = 5432
    ECHO: bool = False
    ENGINE_OPTIONS: dict[str, Any] = {
        "pool_size": 10,
        "pool_pre_ping": True,
    }


class SQLite(Config):
    """Uses for SQLite database server."""

    ECHO: bool = True
    DB_NAME: str = "pypi.sqlite"
    ENGINE_OPTIONS: dict[str, Any] = {
        "pool_pre_ping": True,
    }


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
    CORS_HEADERS: list[str]

    APP_VERSION: str = "1"
