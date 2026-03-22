
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import init_db, get_session

from app.routers.users import router as users_router
from app.routers.auth import router as auth_router

from app.exceptions.auth_exceptions import AuthUserLocked, AuthInvalidCredentiasl


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Arranque
    await init_db()
    yield
    # Apagado (si necesitas cerrar pools, etc.)


app = FastAPI(title="Auth FastAPI", lifespan=lifespan)


app.include_router(users_router)
app.include_router(auth_router)

@app.on_event("startup")
async def on_startup():
    await init_db()

# Añade este bloque a tu main.py
@app.exception_handler(AuthUserLocked)
async def auth_user_locked_handler(request: Request, exc: AuthUserLocked):
    return JSONResponse(
        status_code=403, # 403 Forbidden es adecuado para cuentas bloqueadas
        content={"detail": "La cuenta de usuario está bloqueada. Contacta con soporte."},
    )

# Añade este bloque a tu main.py
@app.exception_handler(AuthInvalidCredentiasl)
async def auth_user_locked_handler(request: Request, exc: AuthInvalidCredentiasl):
    return JSONResponse(
        status_code=401, # 403 Forbidden es adecuado para cuentas bloqueadas
        content={"detail": "Las credenciales que has introducido no son validas"},
    )

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
