import pytest
from httpx import AsyncClient


async def test_register_success(client: AsyncClient):
    response = await client.post(
        "/auth/register", json={"email": "user@example.com", "password": "secret123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "user@example.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


async def test_register_duplicate_email(client: AsyncClient):
    payload = {"email": "dup@example.com", "password": "secret123"}
    await client.post("/auth/register", json=payload)
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 400


async def test_login_success(client: AsyncClient):
    await client.post(
        "/auth/register", json={"email": "login@example.com", "password": "secret123"}
    )
    response = await client.post(
        "/auth/login", data={"username": "login@example.com", "password": "secret123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/auth/register", json={"email": "wrong@example.com", "password": "secret123"}
    )
    response = await client.post(
        "/auth/login",
        data={"username": "wrong@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_protected_route_without_token(client: AsyncClient):
    response = await client.get("/projects/")
    assert response.status_code == 401
