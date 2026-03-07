from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, select
from app.core.config import settings
from app.core.db import get_session, init_db
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title=settings.APP_NAME)


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
