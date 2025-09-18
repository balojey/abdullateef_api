import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from abdullateef_api.db.base import Base
from abdullateef_api.db.enums import BookingStatusEnum, CountryEnum


class Booking(Base):
    """Booking Model."""

    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id"),
        nullable=False,
    )
    package_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hajj_packages.id"),
        nullable=False,
    )
    agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id"),
        nullable=True,
    )
    travelling_from: Mapped[CountryEnum] = mapped_column(
        SQLAEnum(CountryEnum),
        nullable=True,
    )
    status: Mapped[BookingStatusEnum] = mapped_column(
        SQLAEnum(BookingStatusEnum),
        default=BookingStatusEnum.REGISTERED,
        nullable=False,
    )
    moved_to_booking_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # relationships
    client: Mapped["Client"] = relationship("Client", back_populates="bookings")  # type: ignore
    package: Mapped["HajjPackage"] = relationship(  # type: ignore
        "HajjPackage",
        back_populates="bookings",
    )
    agent: Mapped[Optional["Agent"]] = relationship("Agent", back_populates="bookings")  # type: ignore
    payments: Mapped[List["PaymentTransaction"]] = relationship(  # type: ignore
        "PaymentTransaction",
        back_populates="booking",
    )
    commissions: Mapped[List["Commission"]] = relationship(  # type: ignore
        "Commission",
        back_populates="booking",
    )
    moved_to_booking: Mapped[Optional["Booking"]] = relationship(
        "Booking",
        remote_side=[id],
        uselist=False,
    )
