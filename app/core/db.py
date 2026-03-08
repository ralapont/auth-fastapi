from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = async_sessionmaker(
    engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


async def init_db():
    """
    Clase de configuración de la aplicación.

    Atributos:
        database_url (str): URL de conexión a la base de datos.
        debug (bool): Indica si la aplicación corre en modo debug.
        secret_key (str): Clave secreta utilizada para la seguridad.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    """
    Proporciona una sesión asíncrona de base de datos para ser utilizada en
    endpoints o servicios.

    La función actúa como una dependencia de FastAPI: abre una sesión usando
    `SessionLocal()` dentro de un contexto asíncrono y la va entregando con
    `yield`, permitiendo que FastAPI gestione correctamente su ciclo de vida.
    Una vez completada la operación del endpoint, la sesión se cierra
    automáticamente.

    Yields:
        AsyncSession: Sesión de base de datos lista para ejecutar consultas.
    """
    async with SessionLocal() as session:
        yield session
