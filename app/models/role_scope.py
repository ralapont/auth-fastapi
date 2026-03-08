from __future__ import annotations

from sqlmodel import SQLModel, Field


class RoleScope(SQLModel, table=True):
    __tablename__ = "role_scope"

    role_id: int = Field(foreign_key="role.id", primary_key=True)
    scope_id: int = Field(foreign_key="scope.id", primary_key=True)