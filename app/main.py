
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import init_db, get_session
from app.routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Arranque
    await init_db()
    yield
    # Apagado (si necesitas cerrar pools, etc.)


app = FastAPI(title="Auth FastAPI", lifespan=lifespan)
app.include_router(users_router)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/health/db")
async def db_health(session: AsyncSession = Depends(get_session)):
    from sqlalchemy import text
    result = await session.execute(text("SELECT 1"))
    ok = result.scalar() == 1
    return {"status": "ok" if ok else "degraded"}

@app.get("/whoami")
def whoami():
    return {
        "app": settings.APP_NAME,
        "db": settings.DATABASE_URL
    }
