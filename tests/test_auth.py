from httpx import AsyncClient, ASGITransport
import pytest
from api.main import create_app

@pytest.fixture
def app(db):
    app = create_app()
    app.state.test_db = db
    return app

@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_register(client):
    resp = await client.post("/api/auth/register", json={"username": "testuser", "password": "password123"})
    assert resp.status_code == 200
    assert "set-cookie" in resp.headers

@pytest.mark.asyncio
async def test_register_duplicate(client):
    await client.post("/api/auth/register", json={"username": "dupuser", "password": "password123"})
    resp = await client.post("/api/auth/register", json={"username": "dupuser", "password": "password123"})
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "USERNAME_TAKEN"

@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json={"username": "loguser", "password": "password123"})
    resp = await client.post("/api/auth/login", json={"username": "loguser", "password": "wrongpass"})
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_me_unauthorized(client):
    resp = await client.get("/api/me")
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_me_authorized(client):
    resp = await client.post("/api/auth/register", json={"username": "meuser", "password": "password123"})
    assert resp.status_code == 200
    resp = await client.get("/api/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "meuser"
