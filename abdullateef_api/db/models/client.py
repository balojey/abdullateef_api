import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from abdullateef_api.db.base import Base
from abdullateef_api.db.enums import CountryEnum, GenderEnum


class Client(Base):
    """Client Model."""

    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    other_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sex: Mapped[GenderEnum] = mapped_column(SQLAEnum(GenderEnum), nullable=False)
    phone_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )  # E.164 recommended
    passport_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    date_of_birth: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    location: Mapped[CountryEnum] = mapped_column(
        SQLAEnum(CountryEnum),
        nullable=False,
    )  # current location
    referee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # relationships (use string names to avoid circular imports)
    bookings: Mapped[List["Booking"]] = relationship(  # type: ignore
        "Booking",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    referee: Mapped[Optional["Agent"]] = relationship(  # type: ignore
        "Agent",
        back_populates="referred_clients",
        foreign_keys=[referee_id],
    )
    notes: Mapped[List["Note"]] = relationship(  # type: ignore
        "Note",
        back_populates="client",
        cascade="all, delete-orphan",
    )
