from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.user import User
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

from app.core.token_store_redis import (
    register_refresh,
    is_jti_revoked,
    invalidate_refresh,
    revoke_family,
    revoke_jti,
    take_refresh_metadata,
    family_is_revoked
)

# -----------------------------
#  Utilidades internas
# -----------------------------
   
def _get_epoch(payload: Dict[str, Any]) -> int:
    exp = payload["exp"]
    if isinstance(exp, int):
        return exp
    return int(exp.timestamp())

def _now_epoch() -> int:
    return int(datetime.now(timezone.utc).timestamp())

# -----------------------------
#  Servicio de Usuarios (DB)
# -----------------------------

async def get_user_by_username(
    session: AsyncSession,
    username: str
) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

# -----------------------------
#  LOGIN
# -----------------------------

async def login_user(
    session: AsyncSession,
    username: str,
    password: str
) -> Dict[str, str]:
    user = await get_user_by_username(session, username)

    if not user or not verify_password(password, user.password_hash):

        if user:
            if not user.is_active:
                return "userLocked"
            
            user.retry_count += 1
            user.lastLogin_at = datetime.now(timezone.utc)

            if user.retry_count == 5:
                user.is_active = False

            session.add(user)
            await session.commit()
            await session.refresh(user)

            return "userInvalidCredentials"

    # ⏱️ Actualizamos lastLogin_at
    user.lastLogin_at = datetime.now(timezone.utc)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Familia de tokens (sesión completa)
    family_id = str(uuid4())

    claims = {
        "name": user.fullName,
        "email": user.email,
        "roles": [r.name for r in user.roles]
    }

    access = create_access_token(user.username, family_id, claims)
    refresh = create_refresh_token(user.username, family_id)

    # Registrar refresh en Redis
    r_payload = decode_token(refresh)

    await register_refresh(
        jti=r_payload["jti"],
        sub=r_payload["sub"],
        family_id=r_payload["family"],
        exp_ts=_get_epoch(r_payload)
    )

    return {
        "access": access,
        "refresh": refresh,
    }

# -----------------------------
#  REFRESH
# -----------------------------

async def refresh_tokens(
    session: AsyncSession,
    refresh_token: str
) -> Optional[str]:

    payload = decode_token(refresh_token)

    print("REFRESH PAYLOAD =", payload)
    print("IS_REVOKED =", await is_jti_revoked(payload["jti"]))
    print("FAMILY_REVOKED =", await family_is_revoked(payload["family"]))
    print("REDIS META =", await take_refresh_metadata(payload["jti"]))

    if payload.get("scope") != "refresh":
        return None

    jti = payload["jti"]
    family_id = payload["family"]

    if await is_jti_revoked(jti):
        return None

    if await family_is_revoked(family_id):
        return None

    username = payload["sub"]

    # Validar que el refresh esté registrado en Redis
    meta = await take_refresh_metadata(jti)
    if not meta:
        return None

    # Obtener usuario de BD
    user = await get_user_by_username(session, username)
    if not user or not user.is_active:
        return None

    # ROTACIÓN
    await invalidate_refresh(jti, _get_epoch(payload))

    # generar nuevos tokens
    claims = {
        "name": user.fullName,
        "email": user.email,
        "roles": [r.name for r in user.roles]
    }

    new_access = create_access_token(username, family_id, claims)
    new_refresh = create_refresh_token(username, family_id)

    # Registrar refresh nuevo
    new_payload = decode_token(new_refresh)
    await register_refresh(
        jti=new_payload["jti"],
        sub=username,
        family_id=family_id,
        exp_ts=_get_epoch(new_payload)
    )

    return {
        "access": new_access,
        "refresh": new_refresh
    }

# -----------------------------
#  LOGOUT
# -----------------------------

async def logout_user(access_token: str) -> bool:
    payload = decode_token(access_token)

    if payload.get("scope") != "access":
        return False

    # Revocar access actual
    await revoke_jti(payload["jti"], _get_epoch(payload))

    # Revocar familia completa
    family_id = payload["family"]
    ttl_sec = 86400 * 7 * 2  # 2 semanas, configurable
    await revoke_family(family_id, ttl_sec)

    return True

# -----------------------------
#  CURRENT USER
# -----------------------------

async def get_current_user(
    session: AsyncSession,
    access_token: str
) -> Optional[User]:
    try:
        payload = decode_token(access_token)

        if payload.get("scope") != "access":
            return None

        if await is_jti_revoked(payload["jti"]):
            return None

        username = payload["sub"]

        user = await get_user_by_username(session, username)
        if not user or not user.is_active:
            return None

        return user

    except Exception:
        return None
    
