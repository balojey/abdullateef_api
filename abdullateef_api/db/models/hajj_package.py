# abdullateef_api/db/models/hajj_package.py
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from abdullateef_api.db.base import Base


class HajjPackage(Base):
    """Hajj Package Model."""

    __tablename__ = "hajj_packages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    local_price: Mapped[int] = mapped_column(Integer, nullable=False)  # full fee
    diaspora_price: Mapped[int] = mapped_column(Integer, nullable=False)  # full fee
    registration_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    commission_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )  # per-client commission for that year
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    bookings: Mapped[List["Booking"]] = relationship(  # type: ignore
        "Booking",
        back_populates="package",
    )
