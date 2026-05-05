from httpx import AsyncClient

from tests.helpers import (
    add_project_member,
    authorize,
    create_owner_project_with_material,
    register_user,
    login_user,
)


async def test_create_list_and_delete_delivery_recalculates_stock(client: AsyncClient):
    setup = await create_owner_project_with_material(client)
    material_id = setup["material"]["id"]

    response = await client.post(
        "/deliveries/",
        json={
            "material_id": material_id,
            "quantity": 25.5,
            "supplier": "ООО Поставка",
            "comment": "Первая партия",
        },
    )
    assert response.status_code == 201
    delivery = response.json()
    assert delivery["material_id"] == material_id
    assert delivery["quantity"] == 25.5
    assert delivery["supplier"] == "ООО Поставка"

    response = await client.get("/deliveries/", params={"material_id": material_id})
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [delivery["id"]]

    response = await client.get(f"/materials/{material_id}")
    assert response.status_code == 200
    assert response.json()["current_stock"] == 25.5

    response = await client.delete(f"/deliveries/{delivery['id']}")
    assert response.status_code == 204

    response = await client.get(f"/materials/{material_id}")
    assert response.status_code == 200
    assert response.json()["current_stock"] == 0.0


async def test_viewer_can_list_but_cannot_create_or_delete_delivery(
    client: AsyncClient,
):
    setup = await create_owner_project_with_material(client)
    project_id = setup["project"]["id"]
    material_id = setup["material"]["id"]

    delivery_r = await client.post(
        "/deliveries/", json={"material_id": material_id, "quantity": 10.0}
    )
    assert delivery_r.status_code == 201
    delivery_id = delivery_r.json()["id"]

    viewer = await register_user(client, "viewer@test.com")
    viewer_token = await login_user(client, "viewer@test.com")

    authorize(client, setup["owner_token"])
    await add_project_member(client, project_id, viewer["id"], "viewer")

    authorize(client, viewer_token)

    response = await client.get("/deliveries/", params={"material_id": material_id})
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.post(
        "/deliveries/", json={"material_id": material_id, "quantity": 5.0}
    )
    assert response.status_code == 403

    response = await client.delete(f"/deliveries/{delivery_id}")
    assert response.status_code == 403


async def test_create_delivery_requires_auth(client: AsyncClient):
    setup = await create_owner_project_with_material(client)
    client.headers.pop("Authorization", None)

    response = await client.post(
        "/deliveries/",
        json={"material_id": setup["material"]["id"], "quantity": 3.0},
    )

    assert response.status_code == 401
