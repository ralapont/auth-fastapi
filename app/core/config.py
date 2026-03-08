from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """
    Clase de configuración de la aplicación.

    Atributos:
        database_url (str): URL de conexión a la base de datos.
        debug (bool): Indica si la aplicación corre en modo debug.
        secret_key (str): Clave secreta utilizada para la seguridad.
    """
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
        """
        Genera automáticamente la cadena de conexión a la base de datos si el
        usuario no ha proporcionado explícitamente el valor de `DATABASE_URL`.

        Este validador se ejecuta **antes** de asignar el valor al campo
        `DATABASE_URL`. Si el valor (`v`) existe, simplemente se devuelve tal cual.
        Si no existe, el método construye la URL usando otros campos ya validados
        en el modelo (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`)
        accediendo a ellos a través de `info.data`.

        La URL generada utiliza el driver asincrónico `aiomysql` y sigue el
        formato:

            mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}

        Returns:
            str: URL de conexión completa para MySQL usando aiomysql.
        """        
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