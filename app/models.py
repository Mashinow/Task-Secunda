from typing import Optional

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


org_activity_link = Table(
    "org_activity_link",
    Base.metadata,
    Column("organization_id", Integer, ForeignKey("organizations.id"), primary_key=True),
    Column("activity_id", Integer, ForeignKey("activities.id"), primary_key=True),
)


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    address: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    organizations: Mapped[list["Organization"]] = relationship(back_populates="building")


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("activities.id"), nullable=True, index=True)
    depth: Mapped[int] = mapped_column(Integer, default=1)

    parent: Mapped[Optional["Activity"]] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list["Activity"]] = relationship(back_populates="parent")
    organizations: Mapped[list["Organization"]] = relationship(
        secondary=org_activity_link, back_populates="activities"
    )


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), index=True)

    building: Mapped[Building] = relationship(back_populates="organizations")
    activities: Mapped[list[Activity]] = relationship(secondary=org_activity_link, back_populates="organizations")
    phones: Mapped[list["Phone"]] = relationship(back_populates="organization", cascade="all, delete-orphan")


class Phone(Base):
    __tablename__ = "phones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    number: Mapped[str] = mapped_column(String(50))

    organization: Mapped[Organization] = relationship(back_populates="phones")
