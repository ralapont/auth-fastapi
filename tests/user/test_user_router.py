import pytest
from httpx import AsyncClient
from app.schemas.user import UserRegisterIn

@pytest.mark.asyncio
async def test_router_register(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "username": "router",
            "email": "router@example.com",
            "password": "12345678",
            "fullName": "Router Test",
            "phone": "123",
            "roles": ["user"]
        }
        resp = await ac.post("/v1/user/register", json=payload)

    if resp.status_code != 201:
        print("STATUS:", resp.status_code)
        print("RESPONSE:", resp.text)
        print("JSON:", resp.json())

    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "router"


@pytest.mark.asyncio
async def test_router_get_user(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "username": "juan",
            "email": "juan@example.com",
            "password": "12345678",
            "fullName": "Juan",
            "phone": "123",
            "roles": ["user"]
        }
        r1 = await ac.post("/v1/user/register", json=payload)
        uid = r1.json()["id"]

        r2 = await ac.get(f"/v1/user/{uid}")

        assert r2.status_code == 200
        assert r2.json()["username"] == "juan"


@pytest.mark.asyncio
async def test_router_delete_user(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "username": "delete",
            "email": "delete@example.com",
            "password": "12345678",
            "fullName": "Del",
            "phone": "000",
            "roles": ["user"]
        }
        r1 = await ac.post("/v1/user/register", json=payload)
        uid = r1.json()["id"]

        r2 = await ac.delete(f"/v1/user/{uid}")
        assert r2.status_code == 204

        r3 = await ac.get(f"/v1/user/{uid}")
        assert r3.status_code == 404