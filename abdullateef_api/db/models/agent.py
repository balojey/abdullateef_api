import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, String
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from abdullateef_api.db.base import Base
from abdullateef_api.db.enums import GenderEnum


class Agent(Base):
    """Agent Model."""

    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    other_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sex: Mapped[GenderEnum] = mapped_column(SQLAEnum(GenderEnum), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(30), nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    agent_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # relationships
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="agent")  # type: ignore
    commissions: Mapped[List["Commission"]] = relationship(  # type: ignore
        "Commission",
        back_populates="agent",
    )
    referred_clients: Mapped[List["Client"]] = relationship(  # type: ignore
        "Client",
        back_populates="referee",
        foreign_keys="[Client.referee_id]",
    )
