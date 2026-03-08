from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from .user_role import UserRole
from .role_scope import RoleScope

if TYPE_CHECKING:
    from .user import User
    from .scope import Scope

class Role(SQLModel, table=True):
    __tablename__ = "role"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    # Objetivo explícito en Relationship para evitar "list['User']"
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)
    scopes: List["Scope"] = Relationship(back_populates="roles", link_model=RoleScope)    
