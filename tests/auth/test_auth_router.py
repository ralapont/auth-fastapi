import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.routers.auth import get_auth_service
# 1. Importa la dependencia de seguridad (ajusta la ruta si es necesario)
from app.utils.dependencies import get_current_admin_user 

@pytest.mark.asyncio
async def test_unlock_user_endpoint():
    # 2. Mock del Servicio
    mock_service = AsyncMock()
    # Importante: Simular que el servicio devuelve un objeto con atributo username
    mock_user_returned = MagicMock()
    mock_user_returned.username = "ione.belarra@server.com"
    mock_service.restore_user_access.return_value = mock_user_returned

    # 3. Sobrescribir TODAS las dependencias necesarias
    # Sobrescribimos el servicio
    app.dependency_overrides[get_auth_service] = lambda: mock_service
    
    # Sobrescribimos la seguridad: devolvemos un usuario dummy directamente
    # Esto evita que se ejecute la validación real del JWT
    app.dependency_overrides[get_current_admin_user] = lambda: MagicMock(username="admin_test")

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 4. Ejecutar petición (el token ya no importa, pero lo dejamos por estructura)
        response = await ac.post("/auth/unlock/22", headers={"Authorization": "Bearer fake_token"})

    # 5. Aserciones
    assert response.status_code == 200
    # Ajusta el mensaje según lo que devuelva exactamente tu router
    assert "desbloqueado" in response.text.lower() 
    
    # Limpiamos los overrides para no romper otros tests
    app.dependency_overrides.clear()