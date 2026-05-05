from httpx import AsyncClient


async def register_user(
    client: AsyncClient, email: str, password: str = "pass123"
) -> dict:
    response = await client.post(
        "/auth/register", json={"email": email, "password": password}
    )
    assert response.status_code == 201
    return response.json()


async def login_user(
    client: AsyncClient, email: str, password: str = "pass123"
) -> str:
    response = await client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def authorize(client: AsyncClient, token: str) -> None:
    client.headers["Authorization"] = f"Bearer {token}"


async def create_project(client: AsyncClient, name: str = "Тестовый проект") -> dict:
    response = await client.post("/projects/", json={"name": name})
    assert response.status_code == 201
    return response.json()


async def add_project_member(
    client: AsyncClient, project_id: int, user_id: int, role: str
) -> dict:
    response = await client.post(
        f"/projects/{project_id}/members/",
        json={"user_id": user_id, "role": role},
    )
    assert response.status_code == 201
    return response.json()


async def create_material(
    client: AsyncClient,
    project_id: int,
    name: str = "Цемент",
    unit: str = "мешок",
    low_stock_threshold: float = 10.0,
) -> dict:
    response = await client.post(
        "/materials/",
        json={
            "name": name,
            "unit": unit,
            "project_id": project_id,
            "low_stock_threshold": low_stock_threshold,
        },
    )
    assert response.status_code == 201
    return response.json()


async def create_owner_project_with_material(client: AsyncClient) -> dict:
    await register_user(client, "owner@test.com")
    owner_token = await login_user(client, "owner@test.com")
    authorize(client, owner_token)

    project = await create_project(client)
    material = await create_material(client, project["id"])

    return {"owner_token": owner_token, "project": project, "material": material}
