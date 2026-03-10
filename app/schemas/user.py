from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from typing import List, Optional


class RoleScopeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    scopes: List[RoleScopeOut] = []

class UserRegisterIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    fullName: str | None = None 
    phone: str | None = None     
    roles: List[str] = Field(default_factory=lambda: ["user"])

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    fullName: str 
    phone: str          
    roles: List[RoleOut] = []


class UserUpdateIn(BaseModel):
    """
    PUT parcial (no modifica contraseña).
    Si quieres que PUT sea “reemplazo completo”, vuelve obligatorios los campos.
    """
    model_config = ConfigDict(extra="forbid")
    username: Optional[str] = Field(default=None, min_length=3)
    email: Optional[EmailStr] = None
    fullName: Optional[str] = None
    phone: Optional[str] = None
    roles: Optional[List[str]] = None  # None: no tocar; lista vacía: quitar todas

    # Esto es CRÍTICO en Pydantic 2 para que acepte objetos de SQLAlchemy
    model_config = {"from_attributes": True}

