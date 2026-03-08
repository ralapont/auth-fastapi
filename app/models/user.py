from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from .role import Role                # ✅ Import real, NO forward ref
from .user_role import UserRole

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)

    fullName: str | None = Field(default=None, max_length=200) # fullName en la DB
    phone: str | None = Field(default=None, max_length=50)

    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRole)
