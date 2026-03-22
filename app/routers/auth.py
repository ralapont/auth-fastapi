from fastapi import APIRouter, Depends, HTTPException, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.utils.dependencies import get_current_admin_user
from app.core.db import get_session

from app.exceptions.auth_exceptions import AuthUserLocked, AuthInvalidCredentiasl

from app.schemas.auth import LoginRequest, TokenPair, AccessToken, MeResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

# Instanciamos para importar en los routers
async def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)

def _bearer(header: str | None) -> str | None:
    if not header:
        return None
    scheme, _, token = header.partition(" ")
    return token if scheme.lower() == "bearer" else None

@router.post("/login", response_model=TokenPair)
async def login(data: LoginRequest, service: AuthService = Depends(get_auth_service)):
    tokens = await service.login_user(data.username, data.password)
    if tokens == "userLocked":
        raise AuthUserLocked
    if tokens == "userInvalidCredentials":
        raise AuthInvalidCredentiasl
    
    if not tokens:
        raise HTTPException(401, "Invalid credentials")
    return TokenPair(
        access_token=tokens["access"],
        refresh_token=tokens["refresh"]
    )

@router.post("/refresh", response_model=AccessToken, 
    openapi_extra={
        "security": [{"bearerAuth": []}]
    }
)
async def refresh(authorization: Optional[str] = Header(None), service: AuthService = Depends(get_auth_service)):
    print("AUTH HEADER RAW =", authorization)
    token = _bearer(authorization)
    if not token:
        raise HTTPException(401, "Missing refresh token")
    tokens = await service.refresh_tokens(token)
    if not tokens:
        raise HTTPException(401, "Invalid refresh token")
    return AccessToken(access_token=tokens["access"])

@router.post("/logout", status_code=204)
async def logout(authorization: str | None = Header(None), service: AuthService = Depends(get_auth_service)):
    token = _bearer(authorization)
    if not token:
        raise HTTPException(401, "Missing access token")
    ok = await service.logout_user(token)
    if not ok:
        raise HTTPException(401, "Invalid token")
    return Response(status_code=204)

@router.get("/me", response_model=MeResponse)
async def me(authorization: str | None = Header(None), service: AuthService = Depends(get_auth_service)):
    token = _bearer(authorization)
    if not token:
        raise HTTPException(401, "Missing access token")

    user = await service.get_current_user(token)
    if not user:
        raise HTTPException(401, "Invalid token")

    return MeResponse(
        username=user.username,
        full_name=user.fullName,
        email=user.email,
        roles=[r.name for r in user.roles]
    )

@router.post("/unlock/{user_id}")
async def restore_user_endpoint(
    user_id: int,
    service: AuthService = Depends(get_auth_service),
    admin = Depends(get_current_admin_user)
):
    # Aquí le pasas la sesión 'db' que FastAPI te dio arriba
    user = await service.unlock(user_id=user_id)
    
    return {"message": f"Usuario {user.email} desbloqueado"}