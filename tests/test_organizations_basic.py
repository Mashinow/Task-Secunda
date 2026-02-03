import pytest


@pytest.mark.asyncio
async def test_create_and_get_organization(client):
    b = await client.post(
        "/buildings",
        json={"address": "Org street", "latitude": 50.0, "longitude": 30.0},
    )
    building_id = b.json()["id"]
    a = await client.post("/activities", json={"name": "Food"})
    activity_id = a.json()["id"]

    org_resp = await client.post(
        "/organizations",
        json={
            "name": "Pizza Place",
            "building_id": building_id,
            "phones": ["12345"],
            "activity_ids": [activity_id],
        },
    )
    assert org_resp.status_code == 201
    org_id = org_resp.json()["id"]

    resp = await client.get(f"/organizations/{org_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Pizza Place"
    assert len(data["phones"]) == 1
    assert len(data["activities"]) == 1
