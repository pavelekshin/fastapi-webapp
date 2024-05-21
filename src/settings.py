from src.config.config import BaseConfig, Config, CookieConfig, SQLite

# default postgresql docker settings
cfg: Config = SQLite()
settings = BaseConfig()
cookie_settings = CookieConfig()
