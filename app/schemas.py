from typing import Optional

from pydantic import BaseModel, Field


class BuildingOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    address: str
    latitude: float
    longitude: float


class ActivityOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    parent_id: Optional[int]
    depth: int


class OrganizationOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    phones: list[str]
    building: BuildingOut
    activities: list[ActivityOut]


class BuildingCreate(BaseModel):
    address: str
    latitude: float
    longitude: float


class ActivityCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None


class OrganizationCreate(BaseModel):
    name: str
    building_id: int
    phones: list[str] = Field(default_factory=list)
    activity_ids: list[int] = Field(default_factory=list)
