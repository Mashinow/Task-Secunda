import math

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activity, Organization
from app.schemas import OrganizationOut


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


async def collect_descendant_ids(session: AsyncSession, activity_id: int) -> list[int]:
    ids: list[int] = []
    stack = [activity_id]
    while stack:
        current = stack.pop()
        ids.append(current)
        result = await session.execute(
            select(Activity.id).where(Activity.parent_id == current)
        )
        stack.extend(row[0] for row in result.fetchall())
    return ids


def serialize_org(org: Organization) -> OrganizationOut:
    return OrganizationOut(
        id=org.id,
        name=org.name,
        phones=[p.number for p in org.phones],
        building=org.building,
        activities=org.activities,
    )
