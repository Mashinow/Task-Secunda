import pytest


@pytest.mark.asyncio
async def test_create_and_list_buildings(client):
    resp = await client.post(
        "/buildings",
        json={
            "address": "Test street",
            "latitude": 55.75,
            "longitude": 37.61,
        },
    )
    assert resp.status_code == 201
    building = resp.json()
    assert building["id"]

    resp = await client.get("/buildings")
    assert resp.status_code == 200
    buildings = resp.json()
    assert len(buildings) == 1
    assert buildings[0]["address"] == "Test street"
