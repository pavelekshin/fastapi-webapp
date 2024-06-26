from src.config.config import BaseConfig, CookieConfig, PostgreSQL

# default postgresql docker settings
settings = BaseConfig()
db_settings = PostgreSQL(url=str(settings.DATABASE_URL))
cookie_settings = CookieConfig()
