# Test user-related functionality
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app


@pytest.mark.asyncio
async def test_user_api_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create a user
        create_resp = await client.post(
            "/users", json={"email": "khanhpro@gmail.com", "name": "Khanh"}
        )
        assert create_resp.status_code == 200
        created_user = create_resp.json()
        user_id = created_user["id"]
        assert created_user["email"] == "khanhpro@gmail.com"

        # 2. Get all users
        get_all_resp = await client.get("/users")
        assert get_all_resp.status_code == 200
        users = get_all_resp.json()
        assert any(u["id"] == user_id for u in users)

        # 3. Get single user
        get_user_resp = await client.get(f"/users/{user_id}")
        assert get_user_resp.status_code == 200
        user_data = get_user_resp.json()
        assert user_data["email"] == "khanhpro@gmail.com"

        # 4. Login user
        login_resp = await client.post(
            "/auths/login", json={"email": "khanhpro@gmail.com", "name": "Khanh"}
        )
        assert login_resp.status_code == 200
        token_data = login_resp.json()
        assert "token" in token_data
