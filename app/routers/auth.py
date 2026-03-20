from fastapi import APIRouter, Depends, HTTPException, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.db import get_session
from app.services.auth_service import (
    login_user,
    refresh_tokens,
    logout_user,
    get_current_user
)

from app.schemas.auth import LoginRequest, TokenPair, AccessToken, MeResponse

router = APIRouter(prefix="/auth", tags=["auth"])

def _bearer(header: str | None) -> str | None:
    if not header:
        return None
    scheme, _, token = header.partition(" ")
    return token if scheme.lower() == "bearer" else None

@router.post("/login", response_model=TokenPair)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    tokens = await login_user(session, data.username, data.password)

    if not tokens:
        raise HTTPException(401, "Invalid credentials")
    if tokens == "blocked":
        raise HTTPException(403, "Account blocked due to too many failed attempts")

    return TokenPair(
        access_token=tokens["access"],
        refresh_token=tokens["refresh"]
    )

@router.post("/refresh", response_model=AccessToken, 
    openapi_extra={
        "security": [{"bearerAuth": []}]
    }
)
async def refresh(authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    print("AUTH HEADER RAW =", authorization)
    token = _bearer(authorization)
    if not token:
        raise HTTPException(401, "Missing refresh token")
    tokens = await refresh_tokens(session, token)
    if not tokens:
        raise HTTPException(401, "Invalid refresh token")
    return AccessToken(access_token=tokens["access"])

@router.post("/logout", status_code=204)
async def logout(authorization: str | None = Header(None)):
    token = _bearer(authorization)
    if not token:
        raise HTTPException(401, "Missing access token")
    ok = await logout_user(token)
    if not ok:
        raise HTTPException(401, "Invalid token")
    return Response(status_code=204)

@router.get("/me", response_model=MeResponse)
async def me(authorization: str | None = Header(None), session: AsyncSession = Depends(get_session)):
    token = _bearer(authorization)
    if not token:
        raise HTTPException(401, "Missing access token")

    user = await get_current_user(session, token)
    if not user:
        raise HTTPException(401, "Invalid token")

    return MeResponse(
        username=user.username,
        full_name=user.fullName,
        email=user.email,
        roles=[r.name for r in user.roles]
    )