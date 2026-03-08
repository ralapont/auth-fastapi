from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List

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
    roles: List[str] = []

    # Esto es CRÍTICO en Pydantic 2 para que acepte objetos de SQLAlchemy
    model_config = {"from_attributes": True}
