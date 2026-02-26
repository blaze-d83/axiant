from httpx import AsyncClient

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

class TestAuth:
    async def test_login_returns_tokens(self, client: AsyncClient):
        r = await client.post("/auth/mock-login", json={"userId": "alice"})
        assert r.status_code == 200
        assert r.json()["token"].startswith("tok_")

    async def test_same_user_same_token(self, client: AsyncClient):
        t1 = await login(client, "alice")
        t2 = await login(client, "alice")
        assert t1 == t2

