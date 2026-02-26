import pytest #noqa
from httpx import AsyncClient, ASGITransport
from main import app

# ------------------
# Helpers


async def login(client: AsyncClient, user_id: str) -> str:
    r = await client.post("/auth/mock-login", json={"userId": user_id})
    assert r.status_code == 200
    return r.json()["token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ------------------
# Auth


@pytest.mark.asyncio
async def test_login_returns_tokens(self, client: AsyncClient):
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url="/https://test",
            ) as client:
        response = await client.post("/auth/mock-login", json={"userId": "darshan"})

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert isinstance(data["token"], str)

