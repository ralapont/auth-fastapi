import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from jose import jwt, JWTError

from app.models.user import User
from app.core.config import settings
from app.core.db import get_session 

# Creamos un logger específico para este archivo
logger = logging.getLogger("app.dependencies")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decodificar usando settings
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            logger.error("Token decodificado pero el campo 'sub' está vacío")
            raise credentials_exception
        
        logger.info(f"Usuario identificado por token: {username}")
    except JWTError as e:
        logger.warning(f"Fallo en la validación del JWT: {str(e)}")
        raise credentials_exception

    # 2. Búsqueda asíncrona (Ajusta 'id' o 'username' según tu token)
    # Si en el token guardaste el ID:
    statement = select(User).where(User.username == username)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        logger.warning(f"Usuario {username} no encontrado en la base de datos")
        raise credentials_exception
        
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    # Opción A: Si es un string simple en el modelo
    # if current_user.role != "admin":
    
    # Opción B: Si usas la relación de roles que pusiste en el AuthService
    user_roles = [r.name for r in current_user.roles]
    if "admin" not in user_roles:
        logger.warning(f"Acceso denegado: El usuario {current_user.username} NO tiene rol admin. Roles actuales: {user_roles}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Se requieren permisos de administrador"
        )
    
    logger.info(f"Acceso de administrador concedido para: {current_user.username}")        
    return current_user