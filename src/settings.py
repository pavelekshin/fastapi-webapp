from src.config.config import BaseConfig, Config, CookieConfig, PostgreSQL

# default postgresql docker settings
settings = BaseConfig()
db_settings: Config = PostgreSQL(url=str(settings.DATABASE_URL))
cookie_settings = CookieConfig()
