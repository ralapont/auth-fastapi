from __future__ import annotations

import logging
import json
from typing import Optional, Sequence, List

from sqlalchemy import select, exists, and_, delete, insert
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash

from app.models import User, Role, UserRole
from app.schemas.user import UserOut
from app.exceptions.user_exceptions import UserNotFoundError

# Configuramos el logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
    ) -> Optional[UserOut]:
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
        
        response = await self.get_user_by_id(new_user.id)
        
        return response


    async def list_users(self, *, skip: int = 0, limit: int = 50) -> list[UserOut]:
        stmt = (
                select(User)
                .options(
                    selectinload(User.roles).options(
                        selectinload(Role.scopes)
                    )
                )
                .offset(skip)
                .limit(limit)
            )

        result = await self.session.execute(stmt)
        rows = result.scalars().all()

        return [UserOut.model_validate(r, from_attributes=True) for r in rows]


    async def get_user_by_id(self, user_id: int) -> Optional[UserOut]:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.roles).options(
                    selectinload(Role.scopes)
                )
            )
            .limit(1)
        )

        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise UserNotFoundError(f"Usuario con id={user_id} no encontrado")
        return UserOut.model_validate(row, from_attributes=True)


    async def update_user(
        self,
        *,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        fullName: Optional[str] = None,
        phone: Optional[str] = None,
        roles: Optional[List[str]] = None,
    ) -> UserOut:

        # 1) Cargar usuario
        res = await self.session.execute(select(User).where(User.id == user_id).limit(1))
        user = res.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError(f"Usuario con id={user_id} no encontrado")

        # 2) Validar unicidad si cambian username / email
        if username is not None and username != user.username:
            exists_username = await self.session.execute(
                select(exists().where(and_(User.username == username, User.id != user_id)))
            )
            if exists_username.scalar():
                raise UserAlreadyExistsError(f"username '{username}' ya está en uso")

        if email is not None and email != user.email:
            exists_email = await self.session.execute(
                select(exists().where(and_(User.email == email, User.id != user_id)))
            )
            if exists_email.scalar():
                raise UserAlreadyExistsError(f"email '{email}' ya está en uso")

        # 3) Aplicar cambios simples (sin password)
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if fullName is not None:
            user.fullName = fullName
        if phone is not None:
            user.phone = phone


        # 4) Reemplazo de roles (si 'roles' viene en el body)
        if roles is not None:
            # 4.1) Resolver los Role.id desde los nombres
            res_roles = await self.session.execute(
                select(Role.id, Role.name).where(Role.name.in_(roles))
            )
            rows = res_roles.all()
            found_by_name = {name: rid for rid, name in rows}
            missing = [name for name in roles if name not in found_by_name]
            if missing:
                # Usa 404 o 422 según tu semántica
                raise UserNotFoundError(f"Roles no encontrados: {missing}")

            # 4.2) Borrar todas las filas de la asociación del usuario (sin tocar otros datos)
            await self.session.execute(
                delete(UserRole).where(UserRole.user_id == user_id)
            )

            # 4.3) Insertar las nuevas asociaciones (si hay)
            if roles:
                await self.session.execute(
                    insert(UserRole),
                    [{"user_id": user_id, "role_id": found_by_name[name]} for name in roles],
                )

        # 5) Persistir cambios
        await self.session.commit()
        await self.session.flush()

        response = await self.get_user_by_id(user.id)
        
        return response


    async def delete_user(self, user_id: int) -> None:
        # 1) Comprobar existencia
        res = await self.session.execute(select(User).where(User.id == user_id))
        user = res.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError(f"Usuario con id={user_id} no encontrado")

        # 2) Borrar
        await self.session.delete(user)
        await self.session.flush()
        # Si no tienes commit global:
        await self.session.commit()
