from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from .role_scope import RoleScope

if TYPE_CHECKING:
    from .role import Role

class Scope(SQLModel, table=True):
    __tablename__ = "scope"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)

    roles: List["Role"] = Relationship(back_populates="scopes", link_model=RoleScope)