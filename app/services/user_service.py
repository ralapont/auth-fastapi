from __future__ import annotations

import logging
import json
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from app.core.security import get_password_hash

from app.models import User, Role, UserRole

# Configuramos el logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserAlreadyExistsError(Exception):
    """Se lanza cuando username o email ya están registrados."""


class UserService:
    """
    Servicio de dominio para operaciones con usuarios.

    Responsabilidades:
    - Reglas de negocio y validaciones (unicidad, normalización, etc.)
    - Hash de contraseñas
    - Acceso a la capa de persistencia (a través de AsyncSession)
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ---------- Helpers internos ----------

    @staticmethod
    def _roles_to_db(roles: Sequence[str] | None) -> str:
        """Serializa la lista de roles para almacenamiento simple."""
        return json.dumps(list(roles or []))

    @staticmethod
    def _roles_from_db(raw: str | None) -> list[str]:
        """Deserializa los roles almacenados en texto."""
        try:
            return json.loads(raw or "[]")
        except Exception:
            return []

    # ---------- Consultas ----------

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Recupera un usuario por su `username`.

        Returns:
            Optional[User]: El usuario si existe, en caso contrario `None`.
        """
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Recupera un usuario por su `email`.

        Returns:
            Optional[User]: El usuario si existe, en caso contrario `None`.
        """
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_username_or_email(self, username: str, email: str) -> bool:
        """
        Indica si existe ya un registro con el `username` o el `email` dados.

        Returns:
            bool: True si existe alguna coincidencia, False en caso contrario.
        """
        stmt = select(User).where((User.username == username) | (User.email == email))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    # ---------- Comandos (mutaciones) ----------

    async def register_user(
        self,
        *,
        username: str,
        email: str,
        password: str,
        fullName: str | None = None, 
        phone: str | None = None,
        roles: Sequence[str] | None = None,
    ) -> User:
        """
        Registra un nuevo usuario aplicando reglas de negocio:

        - Verifica unicidad de `username` y `email`.
        - Genera `password_hash` con bcrypt.
        - Persiste el usuario.

        Raises:
            UserAlreadyExistsError: Si `username` o `email` ya están en uso.

        Returns:
            User: Instancia persistida con `id` asignado.
        """
        logger.info(f"--- Iniciando registro para: {username} ---")

        # 1) Unicidad
        if await self.exists_username_or_email(username, email):
            raise UserAlreadyExistsError("El username o el email ya están registrados.")

        # 2) Hash de contraseña
        password_hash = get_password_hash(password)

        # 1. Busca los roles SIEMPRE primero
        role_names = roles or ["user"]
        stmt_roles = select(Role).where(Role.name.in_(role_names))
        result = await self.session.execute(stmt_roles)
        
        # AQUÍ se define la variable
        found_roles = result.scalars().all()

        # 1) crear usuario
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            fullName=fullName,
            phone=phone          
        )
        self.session.add(new_user)                  # Re-añadimos para que detecte el cambio en la relación
        # 3. El momento de la verdad (El Flush)
        await self.session.flush()

        for role in found_roles:
            logger.info(f"Asociando User {new_user.id} con Role {role.id} ({role.name})")
            user_role_entry = UserRole(user_id=new_user.id, role_id=role.id)
            self.session.add(user_role_entry)

        await self.session.commit()

        # En lugar de refresh, sacamos los nombres de los roles que ya tenemos
        role_names = [r.name for r in found_roles]
        logger.info("Devolviendo datos al Router...")
        
        response = {
                    "id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "fullName": new_user.fullName,
                    "phone": new_user.phone,
                    "roles": role_names
                }
        
        return response
