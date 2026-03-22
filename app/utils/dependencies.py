from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.models.user import User
from app.core.config import settings
from app.core.db import get_session 

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
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2. Búsqueda asíncrona (Ajusta 'id' o 'username' según tu token)
    # Si en el token guardaste el ID:
    user = await db.get(User, payload.get("user_id")) 
    
    if not user or not user.is_active:
        raise credentials_exception
        
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    # Opción A: Si es un string simple en el modelo
    # if current_user.role != "admin":
    
    # Opción B: Si usas la relación de roles que pusiste en el AuthService
    user_roles = [r.name for r in current_user.roles]
    if "admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Se requieren permisos de administrador"
        )
        
    return current_user