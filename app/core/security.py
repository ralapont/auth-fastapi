import bcrypt

from app.core.config import settings
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from uuid import uuid4
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status

def get_password_hash(password: str) -> str:
    # 1. Convertimos el string a bytes
    password_bytes = password.encode('utf-8')
    # 2. Generamos la sal (salt)
    salt = bcrypt.gensalt(rounds=12, prefix=b"2b")
    # 3. Hasheamos directamente con la librería de C
    hashed = bcrypt.hashpw(password_bytes, salt)
    # 4. Devolvemos como string para la DB
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Comparamos bytes contra el hash guardado
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def _now_utc():
    return datetime.now(timezone.utc)

def create_token(subject: str, expires_delta: timedelta, scope: str, extra: Optional[Dict[str, Any]] = None) -> str:
    now = _now_utc()
    to_encode = {
        "sub": subject,
        "exp": now + expires_delta,
        "iat": now,
        "nbf": now,
        "jti": str(uuid4()),
        "scope": scope,  # "access" | "refresh"
    }
    if extra:
        to_encode.update(extra)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str, family_id: str, extra: Optional[Dict[str, Any]] = None) -> str:
    add = {"family": family_id}
    if extra:
        add.update(extra)
    return create_token(subject, timedelta(minutes=settings.ACCESS_MIN), "access", add)


def create_refresh_token(subject: str, family_id: str) -> str:
    return create_token(subject, timedelta(days=settings.REFRESH_DAYS), "refresh", {"family": family_id})


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
