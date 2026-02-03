import pytest


@pytest.mark.asyncio
async def test_orgs_by_building_and_search(client):
    b = await client.post(
        "/buildings",
        json={"address": "Search st", "latitude": 10.0, "longitude": 10.0},
    )
    building_id = b.json()["id"]

    await client.post(
        "/organizations",
        json={
            "name": "Super Bakery",
            "building_id": building_id,
            "phones": ["111"],
            "activity_ids": [],
        },
    )

    resp = await client.get(f"/organizations/by-building/{building_id}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = await client.get("/organizations/search", params={"name": "bak"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_orgs_by_activity_recursive(client):
    a = await client.post("/activities", json={"name": "Services"})
    a_id = a.json()["id"]

    b = await client.post(
        "/activities",
        json={"name": "Cleaning", "parent_id": a_id},
    )
    b_id = b.json()["id"]

    bld = await client.post(
        "/buildings",
        json={"address": "Clean st", "latitude": 0.0, "longitude": 0.0},
    )
    building_id = bld.json()["id"]

    await client.post(
        "/organizations",
        json={
            "name": "Cleaners",
            "building_id": building_id,
            "phones": [],
            "activity_ids": [b_id],
        },
    )

    resp = await client.get(f"/organizations/by-activity/{a_id}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_orgs_nearby_radius(client):
    b = await client.post(
        "/buildings",
        json={"address": "Geo st", "latitude": 55.75, "longitude": 37.61},
    )
    building_id = b.json()["id"]

    await client.post(
        "/organizations",
        json={
            "name": "GeoOrg",
            "building_id": building_id,
            "phones": [],
            "activity_ids": [],
        },
    )

    resp = await client.get(
        "/organizations/nearby",
        params={
            "lat": 55.75,
            "lng": 37.61,
            "radius_km": 1,
        },
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1
