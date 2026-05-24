from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    SESSION_COOKIE_NAME: str = "sakinfan_session"
    SESSION_TTL_SECONDS: int = 604800
    DEBUG: bool = False

    # Initial Admin Settings
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@sakinfan.com"
    ADMIN_PASSWORD: str = "changeme"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
