from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    APP_ENV: str = "local"
    APP_NAME: str = "auth-service"

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    DATABASE_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def build_url(cls, v, info):
        if v:
            return v

        data = info.data  # así accedemos a los otros campos

        user = data.get("DB_USER")
        pwd = data.get("DB_PASSWORD")
        host = data.get("DB_HOST")
        port = data.get("DB_PORT")
        name = data.get("DB_NAME")

        return f"mysql+aiomysql://{user}:{pwd}@{host}:{port}/{name}"


settings = Settings()