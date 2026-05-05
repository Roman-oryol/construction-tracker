from httpx import AsyncClient

from tests.helpers import (
    add_project_member,
    authorize,
    create_project,
    login_user,
    register_user,
)


async def test_owner_can_add_list_update_and_remove_project_member(
    client: AsyncClient,
):
    await register_user(client, "owner@test.com")
    owner_token = await login_user(client, "owner@test.com")
    member = await register_user(client, "member@test.com")

    authorize(client, owner_token)
    project = await create_project(client)

    response = await client.get(f"/projects/{project['id']}/members/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["role"] == "owner"

    added = await add_project_member(client, project["id"], member["id"], "viewer")
    assert added["role"] == "viewer"

    response = await client.patch(
        f"/projects/{project['id']}/members/{member['id']}",
        json={"user_id": member["id"], "role": "editor"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "editor"

    response = await client.delete(f"/projects/{project['id']}/members/{member['id']}")
    assert response.status_code == 204

    response = await client.get(f"/projects/{project['id']}/members/")
    assert response.status_code == 200
    assert [item["user_id"] for item in response.json()] != [member["id"]]


async def test_non_owner_cannot_manage_project_members(client: AsyncClient):
    await register_user(client, "owner@test.com")
    owner_token = await login_user(client, "owner@test.com")
    editor = await register_user(client, "editor@test.com")
    viewer = await register_user(client, "viewer@test.com")
    outsider = await register_user(client, "outsider@test.com")
    editor_token = await login_user(client, "editor@test.com")

    authorize(client, owner_token)
    project = await create_project(client)
    await add_project_member(client, project["id"], editor["id"], "editor")
    await add_project_member(client, project["id"], viewer["id"], "viewer")

    authorize(client, editor_token)

    response = await client.post(
        f"/projects/{project['id']}/members/",
        json={"user_id": outsider["id"], "role": "viewer"},
    )
    assert response.status_code == 403

    response = await client.patch(
        f"/projects/{project['id']}/members/{viewer['id']}",
        json={"user_id": viewer["id"], "role": "editor"},
    )
    assert response.status_code == 403

    response = await client.delete(f"/projects/{project['id']}/members/{viewer['id']}")
    assert response.status_code == 403


async def test_owner_cannot_duplicate_member_or_change_owner_membership(
    client: AsyncClient,
):
    owner = await register_user(client, "owner@test.com")
    owner_token = await login_user(client, "owner@test.com")
    viewer = await register_user(client, "viewer@test.com")

    authorize(client, owner_token)
    project = await create_project(client)
    await add_project_member(client, project["id"], viewer["id"], "viewer")

    response = await client.post(
        f"/projects/{project['id']}/members/",
        json={"user_id": viewer["id"], "role": "viewer"},
    )
    assert response.status_code == 409

    response = await client.patch(
        f"/projects/{project['id']}/members/{owner['id']}",
        json={"user_id": owner["id"], "role": "editor"},
    )
    assert response.status_code == 403

    response = await client.delete(f"/projects/{project['id']}/members/{owner['id']}")
    assert response.status_code == 403
