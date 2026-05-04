from httpx import AsyncClient


async def test_create_project(auth_client: AsyncClient):
    response = await auth_client.post(
        "/projects/",
        json={"name": "Жилой комплекс Альфа", "address": "ул. Строителей, 1"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Жилой комплекс Альфа"
    assert "id" in data


async def test_get_projects_only_own(client: AsyncClient):
    await client.post(
        "/auth/register", json={"email": "user1@test.com", "password": "pass123"}
    )
    await client.post(
        "/auth/register", json={"email": "user2@test.com", "password": "pass123"}
    )

    r = await client.post(
        "/auth/login", data={"username": "user1@test.com", "password": "pass123"}
    )
    token1 = r.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token1}"
    await client.post("/projects/", json={"name": "Проект user1"})

    r = await client.post(
        "/auth/login", data={"username": "user2@test.com", "password": "pass123"}
    )
    token2 = r.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token2}"
    response = await client.get("/projects/")

    assert response.status_code == 200
    assert response.json() == []


async def test_delete_project_forbidden_for_non_owner(client: AsyncClient):
    await client.post(
        "/auth/register", json={"email": "owner@test.com", "password": "pass123"}
    )
    editor_r = await client.post(
        "/auth/register", json={"email": "editor@test.com", "password": "pass123"}
    )
    editor_id = editor_r.json()["id"]

    r = await client.post(
        "/auth/login", data={"username": "owner@test.com", "password": "pass123"}
    )
    owner_token = r.json()["access_token"]

    r = await client.post(
        "/auth/login", data={"username": "editor@test.com", "password": "pass123"}
    )
    editor_token = r.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {owner_token}"
    project_r = await client.post("/projects/", json={"name": "Тест проект"})
    project_id = project_r.json()["id"]

    await client.post(
        f"/projects/{project_id}/members/",
        json={"user_id": editor_id, "role": "editor"},
    )

    client.headers["Authorization"] = f"Bearer {editor_token}"
    response = await client.delete(f"/projects/{project_id}")
    assert response.status_code == 403
