import logging
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger("AuthService")

    # --- Utilidades internas ---
    def _get_epoch(self, payload: Dict[str, Any]) -> int:
        exp = payload["exp"]
        return exp if isinstance(exp, int) else int(exp.timestamp())

    def _now_epoch(self) -> int:
        return int(datetime.now(timezone.utc).timestamp())

    # --- Métodos de Base de Datos ---

    async def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # --- Lógica de Negocio ---

    async def login_user(self, username: str, password: str) -> Dict[str, str]:
        user = await self.get_user_by_username(username)

        # Validación de credenciales y bloqueo
        if not user or not verify_password(password, user.password_hash):
            if user:
                if not user.is_active:
                    # Aquí es donde lanzamos tu excepción personalizada o una 403
                    raise HTTPException(status_code=403, detail="USER_LOCKED")
                
                user.retry_count += 1
                user.lastLogin_at = datetime.now(timezone.utc)

                if user.retry_count >= 5:
                    user.is_active = False

                self.session.add(user)
                await self.session.commit()
                raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS")
            
            raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS")

        # Login exitoso: Resetear intentos y actualizar fecha
        user.retry_count = 0
        user.lastLogin_at = datetime.now(timezone.utc)
        self.session.add(user)
        await self.session.commit()

        family_id = str(uuid4())
        claims = {
            "name": user.fullName,
            "email": user.email,
            "roles": [r.name for r in user.roles]
        }

        access = create_access_token(user.username, family_id, claims)
        refresh = create_refresh_token(user.username, family_id)

        # Registro en Redis
        r_payload = decode_token(refresh)
        await register_refresh(
            jti=r_payload["jti"],
            sub=r_payload["sub"],
            family_id=r_payload["family"],
            exp_ts=self._get_epoch(r_payload)
        )

        return {"access": access, "refresh": refresh}

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, str]:
        payload = decode_token(refresh_token)

        if payload.get("scope") != "refresh":
            raise HTTPException(status_code=401, detail="INVALID_TOKEN_SCOPE")

        jti, family_id = payload["jti"], payload["family"]

        if await is_jti_revoked(jti) or await family_is_revoked(family_id):
            raise HTTPException(status_code=401, detail="TOKEN_REVOKED")

        # Validar metadata en Redis
        meta = await take_refresh_metadata(jti)
        if not meta:
            raise HTTPException(status_code=401, detail="TOKEN_EXPIRED_OR_NOT_FOUND")

        user = await self.get_user_by_username(payload["sub"])
        if not user or not user.is_active:
            raise HTTPException(status_code=403, detail="USER_INACTIVE")

        # Rotación: Invalidar el viejo y generar nuevos
        await invalidate_refresh(jti, self._get_epoch(payload))

        claims = {"name": user.fullName, "email": user.email, "roles": [r.name for r in user.roles]}
        new_access = create_access_token(user.username, family_id, claims)
        new_refresh = create_refresh_token(user.username, family_id)

        new_payload = decode_token(new_refresh)
        await register_refresh(
            jti=new_payload["jti"],
            sub=user.username,
            family_id=family_id,
            exp_ts=self._get_epoch(new_payload)
        )

        return {"access": new_access, "refresh": new_refresh}

    async def logout_user(self, access_token: str) -> bool:
        payload = decode_token(access_token)
        if payload.get("scope") != "access":
            return False

        await revoke_jti(payload["jti"], self._get_epoch(payload))
        await revoke_family(payload["family"], 1209600) # 2 semanas
        return True

    async def get_current_user(self, access_token: str) -> Optional[User]:
        try:
            payload = decode_token(access_token)
            if payload.get("scope") != "access" or await is_jti_revoked(payload["jti"]):
                return None

            user = await self.get_user_by_username(payload["sub"])
            return user if user and user.is_active else None
        except Exception:
            return None

    async def unlock(self, user_id: int) -> User:

        self.logger.info(f"Intentando restaurar acceso para el usuario ID: {user_id}")

        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        user = await self.get_user_by_id(user_id)
        
        
        if not user:
            self.logger.warning(f"Restauración fallida: Usuario {user_id} no encontrado")
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        self.logger.info(f"Usuario {user.username} encontrado. Estado actual: is_active={user.is_active}")

        # Reset de seguridad
        user.is_active = True
        user.retry_count = 0 
        
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            self.logger.info(f"Usuario {user.username} desbloqueado exitosamente")
        except Exception as e:
            self.logger.error(f"Error en base de datos al restaurar usuario: {str(e)}")
            await self.session.rollback()
            raise e
        
        return user