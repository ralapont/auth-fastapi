# app/routers/users.py
import logging
from typing import List


from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_session

from app.schemas.user import UserOut
from app.schemas.user import UserRegisterIn, UserUpdateIn

from app.models.role import Role
from app.models.user_role import UserRole

from app.services.user_service import UserService
from app.exceptions.user_exceptions import UserAlreadyExistsError, UserNotFoundError

# Configuramos el logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/v1/user", tags=["users"])

async def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses = {
        201: {"model": UserOut},
        409: {"description": "Username o email ya están registrados"}
    },
    summary="Registrar un nuevo usuario",
    response_description="Usuario creado correctamente"
)
async def register_user(payload: UserRegisterIn, service: UserService = Depends(get_user_service)):
    try:

        logger.error(
            "ROUTER captura clase: %s (mod=%s, id=%s)",
            UserAlreadyExistsError, UserAlreadyExistsError.__module__, id(UserAlreadyExistsError)
        )

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
        logger.error(
            "SERVICE va a lanzar: %s (mod=%s, id=%s)",
            UserAlreadyExistsError, UserAlreadyExistsError.__module__, id(UserAlreadyExistsError)
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) 


@router.get(
    "/",
    response_model=List[UserOut],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    response_description="Listado paginado de usuarios"
)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: UserService = Depends(get_user_service),
):
    return await service.list_users(skip = skip, limit = limit)

@router.get(
    "/{id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Obtener un usuario por ID",
    response_description="Usuario encontrado"
)
async def get_user_by_id(
    id: int = Path(..., ge=1, description="Identificador del usuario"),
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.get_user_by_id(id)
        return user
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.put(
    "/{id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un usuario por ID (sin cambiar contraseña)",
    response_description="Usuario actualizado correctamente"
)
async def update_user(
    id: int = Path(..., ge=1, description="Identificador del usuario"),
    payload: UserUpdateIn = ...,
    session: AsyncSession = Depends(get_session),
):
    service = UserService(session)
    try:
        user = await service.update_user(
            user_id=id,
            username=payload.username,
            email=payload.email,
            fullName=payload.fullName,
            phone=payload.phone,
            roles=payload.roles,  # None ⇒ no tocar; [] ⇒ quitar todas; ["admin", ...] ⇒ reemplazar
        )
        return user
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un usuario por ID",
    response_description="Usuario eliminado correctamente"
)
async def delete_user(
    id: int = Path(..., ge=1, description="ID del usuario a eliminar"),
    session: AsyncSession = Depends(get_session),
):
    service = UserService(session)
    try:
        await service.delete_user(id)
        return  # 204 No Content
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

