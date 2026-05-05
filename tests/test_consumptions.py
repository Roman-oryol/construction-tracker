from httpx import AsyncClient

from tests.helpers import (
    add_project_member,
    authorize,
    create_owner_project_with_material,
    register_user,
    login_user,
)


async def test_create_list_and_delete_consumption_recalculates_stock(
    client: AsyncClient,
):
    setup = await create_owner_project_with_material(client)
    material_id = setup["material"]["id"]

    delivery_r = await client.post(
        "/deliveries/", json={"material_id": material_id, "quantity": 40.0}
    )
    assert delivery_r.status_code == 201

    response = await client.post(
        "/consumptions/",
        json={
            "material_id": material_id,
            "quantity": 12.5,
            "brigade": "Бригада 7",
            "comment": "Фундамент",
        },
    )
    assert response.status_code == 201
    consumption = response.json()
    assert consumption["material_id"] == material_id
    assert consumption["quantity"] == 12.5
    assert consumption["brigade"] == "Бригада 7"

    response = await client.get("/consumptions/", params={"material_id": material_id})
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [consumption["id"]]

    response = await client.get(f"/materials/{material_id}")
    assert response.status_code == 200
    assert response.json()["current_stock"] == 27.5

    response = await client.delete(f"/consumptions/{consumption['id']}")
    assert response.status_code == 204

    response = await client.get(f"/materials/{material_id}")
    assert response.status_code == 200
    assert response.json()["current_stock"] == 40.0


async def test_viewer_can_list_but_cannot_create_or_delete_consumption(
    client: AsyncClient,
):
    setup = await create_owner_project_with_material(client)
    project_id = setup["project"]["id"]
    material_id = setup["material"]["id"]

    consumption_r = await client.post(
        "/consumptions/",
        json={"material_id": material_id, "quantity": 4.0},
    )
    assert consumption_r.status_code == 201
    consumption_id = consumption_r.json()["id"]

    viewer = await register_user(client, "viewer@test.com")
    viewer_token = await login_user(client, "viewer@test.com")

    authorize(client, setup["owner_token"])
    await add_project_member(client, project_id, viewer["id"], "viewer")

    authorize(client, viewer_token)

    response = await client.get("/consumptions/", params={"material_id": material_id})
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.post(
        "/consumptions/",
        json={"material_id": material_id, "quantity": 2.0},
    )
    assert response.status_code == 403

    response = await client.delete(f"/consumptions/{consumption_id}")
    assert response.status_code == 403


async def test_create_consumption_requires_auth(client: AsyncClient):
    setup = await create_owner_project_with_material(client)
    client.headers.pop("Authorization", None)

    response = await client.post(
        "/consumptions/",
        json={"material_id": setup["material"]["id"], "quantity": 3.0},
    )

    assert response.status_code == 401
