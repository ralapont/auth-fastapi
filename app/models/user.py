from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import Column, Boolean, Integer, DateTime

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

    isActive: bool = Field(
        default=True,
        sa_column=Column("isActive", Boolean, nullable=False)
    )

    retryCount: int = Field(
        default=0,
        sa_column=Column("retryCount", Integer, nullable=False)
    )

    lastLogin_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column("lastLogin_at", DateTime, nullable=True)
    )

    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRole, sa_relationship_kwargs={"lazy": "selectin"},)
