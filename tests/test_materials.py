# tests/test_materials.py

import pytest
from httpx import AsyncClient


@pytest.fixture
async def project(auth_client: AsyncClient) -> dict:
    response = await auth_client.post(
        "/projects/",
        json={"name": "Тестовый объект", "address": "ул. Тестовая, 1"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def material(auth_client: AsyncClient, project: dict) -> dict:
    response = await auth_client.post(
        "/materials/",
        json={
            "name": "Цемент М400",
            "unit": "мешок",
            "project_id": project["id"],
            "low_stock_threshold": 10.0,  # алерт если меньше 10 мешков
        },
    )
    assert response.status_code == 201
    return response.json()


# --- Базовый CRUD ---


async def test_create_material(auth_client: AsyncClient, project: dict):
    """Новый материал должен иметь нулевой остаток и статус 'critical'
    (stock=0, threshold=10 → 0 <= 0 → critical согласно _calc_status)."""
    response = await auth_client.post(
        "/materials/",
        json={
            "name": "Арматура 12мм",
            "unit": "м",
            "project_id": project["id"],
            "low_stock_threshold": 5.0,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Арматура 12мм"
    assert data["current_stock"] == 0.0
    assert data["stock_status"] == "critical"


async def test_get_material(auth_client: AsyncClient, material: dict):
    response = await auth_client.get(f"/materials/{material['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == material["id"]


async def test_get_materials_list(
    auth_client: AsyncClient, material: dict, project: dict
):
    response = await auth_client.get(
        "/materials/", params={"project_id": project["id"]}
    )
    assert response.status_code == 200
    ids = [m["id"] for m in response.json()]
    assert material["id"] in ids


async def test_update_material(auth_client: AsyncClient, material: dict):
    response = await auth_client.patch(
        f"/materials/{material['id']}",
        json={"name": "Цемент М500", "low_stock_threshold": 20.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Цемент М500"
    assert data["low_stock_threshold"] == 20.0
    assert data["unit"] == material["unit"]  # unit не трогали — должен остаться


async def test_delete_material(auth_client: AsyncClient, material: dict):
    response = await auth_client.delete(f"/materials/{material['id']}")
    assert response.status_code == 204

    response = await auth_client.get(f"/materials/{material['id']}")
    assert response.status_code == 404


# --- Бизнес-логика: расчёт остатка ---


async def test_stock_increases_after_delivery(auth_client: AsyncClient, material: dict):
    await auth_client.post(
        "/deliveries/",
        json={"material_id": material["id"], "quantity": 50.0},
    )
    response = await auth_client.get(f"/materials/{material['id']}")
    assert response.json()["current_stock"] == 50.0


async def test_stock_decreases_after_consumption(
    auth_client: AsyncClient, material: dict
):
    await auth_client.post(
        "/deliveries/",
        json={"material_id": material["id"], "quantity": 50.0},
    )
    await auth_client.post(
        "/consumptions/",
        json={"material_id": material["id"], "quantity": 15.0},
    )
    response = await auth_client.get(f"/materials/{material['id']}")
    assert response.json()["current_stock"] == 35.0


async def test_stock_status_transitions(auth_client: AsyncClient, material: dict):
    # critical: stock=0 при создании
    r = await auth_client.get(f"/materials/{material['id']}")
    assert r.json()["stock_status"] == "critical"

    # low: завозим 5, threshold=10 → 0 < 5 < 10
    await auth_client.post(
        "/deliveries/",
        json={"material_id": material["id"], "quantity": 5.0},
    )
    r = await auth_client.get(f"/materials/{material['id']}")
    assert r.json()["stock_status"] == "low"

    # ok: завозим ещё 10, итого 15 >= 10
    await auth_client.post(
        "/deliveries/",
        json={"material_id": material["id"], "quantity": 10.0},
    )
    r = await auth_client.get(f"/materials/{material['id']}")
    assert r.json()["stock_status"] == "ok"


# --- Авторизация и доступ ---


async def test_create_material_requires_auth(
    client: AsyncClient, auth_client: AsyncClient
):

    project_r = await auth_client.post(
        "/projects/",
        json={"name": "Тестовый объект"},
    )
    project_id = project_r.json()["id"]

    client.headers.pop("Authorization", None)
    response = await client.post(
        "/materials/",
        json={"name": "Кирпич", "unit": "шт", "project_id": project_id},
    )
    assert response.status_code == 401


async def test_cannot_access_other_users_material(client: AsyncClient, material: dict):
    await client.post(
        "/auth/register",
        json={"email": "other@test.com", "password": "pass123"},
    )
    r = await client.post(
        "/auth/login",
        data={"username": "other@test.com", "password": "pass123"},
    )
    client.headers["Authorization"] = f"Bearer {r.json()['access_token']}"

    response = await client.get(f"/materials/{material['id']}")
    assert response.status_code == 404
