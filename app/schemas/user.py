from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from typing import List


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

    # Esto es CRÍTICO en Pydantic 2 para que acepte objetos de SQLAlchemy
    model_config = {"from_attributes": True}
