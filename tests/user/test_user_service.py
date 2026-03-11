import pytest
from app.services.user_service import UserService
from app.exceptions.user_exceptions import UserAlreadyExistsError, UserNotFoundError
from app.schemas.user import UserRegisterIn
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_router_register_ok(app, seed_roles):  # ← usa seed_roles si tu servicio lo requiere
    transport = ASGITransport(app=app)  # evitar deprecation de 'app='
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "username": "router",
            "email": "router@example.com",
            "password": "12345678",
            "fullName": "Router Test",
            "phone": "123",
            "roles": ["user"]        # si roles es obligatorio en tu servicio
        }
        resp = await ac.post("/v1/user/register", json=payload)

    if resp.status_code != 201:
        print("STATUS:", resp.status_code)
        print("RESPONSE:", resp.json())

    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "router"
    assert data["email"] == "router@example.com"

@pytest.mark.asyncio
async def test_get_user_not_found(async_session):
    service = UserService(async_session)

    with pytest.raises(UserNotFoundError):
        await service.get_user_by_id(999)


@pytest.mark.asyncio
async def test_update_user_change_email(async_session):
    service = UserService(async_session)

    # crear uno
    created = await service.register_user(
        username="pepe",
        email="pepe@example.com",
        password="12345678",
        fullName="Pepe",
        phone="999",
        roles=["user"]
    )

    # actualizar
    updated = await service.update_user(
        user_id=created.id,
        email="nuevo@example.com"
    )

    assert updated.email == "nuevo@example.com"


@pytest.mark.asyncio
async def test_delete_user(async_session):
    service = UserService(async_session)

    created = await service.register_user(
        username="borrar",
        email="borrar@example.com",
        password="12345678",
        fullName="Test",
        phone="000",
        roles=["user"]
    )

    await service.delete_user(created.id)

    with pytest.raises(UserNotFoundError):
        await service.get_user_by_id(created.id)