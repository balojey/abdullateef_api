import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from abdullateef_api.db.base import Base
from abdullateef_api.db.enums import CommissionStatusEnum


class Commission(Base):
    """Commission Model."""

    __tablename__ = "commissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id"),
        nullable=False,
    )
    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id"),
        nullable=False,
    )
    commission_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[CommissionStatusEnum] = mapped_column(
        SQLAEnum(CommissionStatusEnum),
        default=CommissionStatusEnum.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    agent: Mapped["Agent"] = relationship("Agent", back_populates="commissions")  # type: ignore
    booking: Mapped["Booking"] = relationship("Booking", back_populates="commissions")  # type: ignore
