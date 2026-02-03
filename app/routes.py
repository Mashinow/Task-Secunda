from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import MAX_ACTIVITY_DEPTH
from app.database import get_session
from app.deps import verify_api_key
from app.models import Activity, Building, Organization, Phone, org_activity_link
from app.schemas import (
    ActivityCreate,
    ActivityOut,
    BuildingCreate,
    BuildingOut,
    OrganizationCreate,
    OrganizationOut,
)
from app.utils import collect_descendant_ids, haversine_km, serialize_org

router = APIRouter(dependencies=[Depends(verify_api_key)])


ORG_OPTIONS = [
    selectinload(Organization.phones),
    selectinload(Organization.building),
    selectinload(Organization.activities),
]


@router.get("/buildings", response_model=list[BuildingOut])
async def list_buildings(session: AsyncSession = Depends(get_session)):
    """Список всех зданий."""
    result = await session.execute(select(Building))
    return result.scalars().all()


@router.post("/buildings", response_model=BuildingOut, status_code=status.HTTP_201_CREATED)
async def create_building(data: BuildingCreate, session: AsyncSession = Depends(get_session)):
    """Создает новое здание."""
    building = Building(**data.model_dump())
    session.add(building)
    await session.commit()
    await session.refresh(building)
    return building


@router.get("/activities", response_model=list[ActivityOut])
async def list_activities(session: AsyncSession = Depends(get_session)):
    """Список всех деятельностей."""
    result = await session.execute(select(Activity))
    return result.scalars().all()


@router.post("/activities", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
async def create_activity(data: ActivityCreate, session: AsyncSession = Depends(get_session)):
    """Создает новую деятельность."""
    depth = 1
    if data.parent_id is not None:
        result = await session.execute(select(Activity).where(Activity.id == data.parent_id))
        parent = result.scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent activity not found")
        depth = parent.depth + 1
        if depth > MAX_ACTIVITY_DEPTH:
            raise HTTPException(status_code=400, detail=f"Max nesting depth is {MAX_ACTIVITY_DEPTH}")

    activity = Activity(name=data.name, parent_id=data.parent_id, depth=depth)
    session.add(activity)
    await session.commit()
    await session.refresh(activity)
    return activity


@router.get("/organizations/by-building/{building_id}", response_model=list[OrganizationOut])
async def orgs_by_building(building_id: int, session: AsyncSession = Depends(get_session)):
    """Все организации в указанном здании."""
    result = await session.execute(select(Building).where(Building.id == building_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Building not found")

    result = await session.execute(
        select(Organization).where(Organization.building_id == building_id).options(*ORG_OPTIONS)
    )
    return [serialize_org(o) for o in result.scalars().all()]


@router.get("/organizations/by-activity/{activity_id}", response_model=list[OrganizationOut])
async def orgs_by_activity(activity_id: int, session: AsyncSession = Depends(get_session)):
    """
    Организации по виду деятельности.
    """
    result = await session.execute(select(Activity).where(Activity.id == activity_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Activity not found")

    all_ids = await collect_descendant_ids(session, activity_id)

    result = await session.execute(
        select(Organization)
        .join(org_activity_link)
        .where(org_activity_link.c.activity_id.in_(all_ids))
        .options(*ORG_OPTIONS)
        .distinct()
    )
    return [serialize_org(o) for o in result.scalars().all()]


@router.get("/organizations/search", response_model=list[OrganizationOut])
async def search_orgs(
    name: str = Query(..., min_length=1),
    session: AsyncSession = Depends(get_session),
):
    """Поиск организаций по названию"""
    result = await session.execute(
        select(Organization)
        .where(Organization.name.ilike(f"%{name}%"))
        .options(*ORG_OPTIONS)
    )
    return [serialize_org(o) for o in result.scalars().all()]


@router.get("/organizations/nearby", response_model=list[OrganizationOut])
async def orgs_nearby(
    lat: float = Query(..., description="Широта центра"),
    lng: float = Query(..., description="Долгота центра"),
    radius_km: Optional[float] = Query(None, description="Радиус в км (круглая область)"),
    min_lat: Optional[float] = Query(None, description="Прямоугольник: мин широта"),
    max_lat: Optional[float] = Query(None, description="Прямоугольник: макс широта"),
    min_lng: Optional[float] = Query(None, description="Прямоугольник: мин долгота"),
    max_lng: Optional[float] = Query(None, description="Прямоугольник: макс долгота"),
    session: AsyncSession = Depends(get_session),
):
    """
    Организации в заданном радиусе
    """
    use_radius = radius_km is not None
    use_rect = all(v is not None for v in [min_lat, max_lat, min_lng, max_lng])

    if not use_radius and not use_rect:
        raise HTTPException(status_code=400, detail="Specify either radius_km or all four rect params")

    result = await session.execute(select(Building))
    buildings = result.scalars().all()

    matched_ids: list[int] = []
    for b in buildings:
        if use_radius:
            if haversine_km(lat, lng, b.latitude, b.longitude) <= radius_km:
                matched_ids.append(b.id)
        else:
            if min_lat <= b.latitude <= max_lat and min_lng <= b.longitude <= max_lng:
                matched_ids.append(b.id)

    if not matched_ids:
        return []

    result = await session.execute(
        select(Organization)
        .where(Organization.building_id.in_(matched_ids))
        .options(*ORG_OPTIONS)
    )
    return [serialize_org(o) for o in result.scalars().all()]


@router.get("/organizations/{org_id}", response_model=OrganizationOut)
async def get_organization(org_id: int, session: AsyncSession = Depends(get_session)):
    """Информация об организации по её ID."""
    result = await session.execute(
        select(Organization).where(Organization.id == org_id).options(*ORG_OPTIONS)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return serialize_org(org)


@router.post("/organizations", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
async def create_organization(data: OrganizationCreate, session: AsyncSession = Depends(get_session)):
    """Создает организацию."""
    result = await session.execute(select(Building).where(Building.id == data.building_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Building not found")

    activities = []
    if data.activity_ids:
        result = await session.execute(select(Activity).where(Activity.id.in_(data.activity_ids)))
        activities = list(result.scalars().all())
        if len(activities) != len(data.activity_ids):
            raise HTTPException(status_code=400, detail="Some activity_ids not found")

    org = Organization(name=data.name, building_id=data.building_id)
    org.phones = [Phone(number=n) for n in data.phones]
    org.activities = activities
    session.add(org)
    await session.commit()
    await session.refresh(org, attribute_names=["phones", "building", "activities"])
    return serialize_org(org)
