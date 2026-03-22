import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.auth_service import AuthService
from app.models.user import User

@pytest.mark.asyncio
async def test_restore_user_access_success():
    # 1. Preparar el Mock de la sesión
    mock_session = AsyncMock()
    user_mock = User(id=22, username="test_user", is_active=False, retry_count=5)
    
    # Simular el resultado de la ejecución del select
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user_mock
    mock_session.execute.return_value = mock_result

    # 2. Ejecutar el servicio
    service = AuthService(mock_session)
    updated_user = await service.unlock(user_id=22)

    # 3. Aserciones
    assert updated_user.is_active is True
    assert updated_user.retry_count == 0
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(user_mock)