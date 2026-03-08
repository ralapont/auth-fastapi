# app/routers/users.py
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_session

from app.schemas.user import UserOut
from app.schemas.user import UserRegisterIn

from app.models.role import Role
from app.models.user_role import UserRole

from app.services.user_service import UserService
from app.exceptions.user_exceptions import UserAlreadyExistsError

router = APIRouter(prefix="/v1/user", tags=["users"])

@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    response_description="Usuario creado correctamente"
)
async def register_user(payload: UserRegisterIn, session: AsyncSession = Depends(get_session)):
    service = UserService(session)

    try:
        user_data = await service.register_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            fullName=payload.fullName, 
            phone=payload.phone,
            roles=payload.roles
        )

        return user_data
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
