import pytest


@pytest.mark.asyncio
async def test_activity_hierarchy(client):
    parent = await client.post("/activities", json={"name": "IT"})
    assert parent.status_code == 201
    parent_id = parent.json()["id"]

    child = await client.post(
        "/activities",
        json={"name": "Web Development", "parent_id": parent_id},
    )
    assert child.status_code == 201

    data = child.json()
    assert data["parent_id"] == parent_id
    assert data["depth"] == 2
