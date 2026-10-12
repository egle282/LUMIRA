import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from jose import jwt

from backend.api.deps import get_current_user
from backend.core.config import settings

@pytest.mark.asyncio
async def test_get_current_user_injects_rls_context():
    """
    REGRESSION TEST: Ensures that get_current_user correctly calls set_tenant_context
    to enforce Row-Level Security (RLS) upon successful authentication.
    """
    mock_db = AsyncMock()
    mock_result = MagicMock()
    
    mock_user = MagicMock()
    mock_user.id = "user_123"
    mock_user.tenant_id = "tenant_abc"
    
    mock_result.scalars().first.return_value = mock_user
    mock_db.execute.return_value = mock_result
    
    valid_token = jwt.encode({"sub": "user_123", "tenant_id": "tenant_abc"}, settings.JWT_SECRET, algorithm="HS256")
    
    with patch("backend.api.deps.set_tenant_context", new_callable=AsyncMock) as mock_set_tenant_context:
        user = await get_current_user(token=valid_token, db=mock_db)
        
        assert user.id == "user_123"
        # Verify the RLS context injection function was called with correct tenant_id
        mock_set_tenant_context.assert_called_once_with(mock_db, "tenant_abc")
