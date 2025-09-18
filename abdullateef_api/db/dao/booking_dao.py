import uuid
from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.models.booking import Booking
from abdullateef_api.db.enums import BookingStatusEnum, CountryEnum


class BookingDAO:
    """Data Access Object for Booking model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ---------- CRUD ----------
    async def create(
        self,
        client_id: uuid.UUID,
        package_id: uuid.UUID,
        agent_id: Optional[uuid.UUID] = None,
        travelling_from: Optional[CountryEnum] = None,
        status: BookingStatusEnum = BookingStatusEnum.REGISTERED,
        moved_to_booking_id: Optional[uuid.UUID] = None,
    ) -> Booking:
        booking = Booking(
            client_id=client_id,
            package_id=package_id,
            agent_id=agent_id,
            travelling_from=travelling_from,
            status=status,
            moved_to_booking_id=moved_to_booking_id,
        )
        self.session.add(booking)
        await self.session.flush()
        return booking

    async def get_by_id(self, booking_id: uuid.UUID) -> Optional[Booking]:
        result = await self.session.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> List[Booking]:
        result = await self.session.execute(select(Booking))
        return result.scalars().all()

    async def delete(self, booking_id: uuid.UUID) -> bool:
        result = await self.session.execute(
            delete(Booking).where(Booking.id == booking_id).returning(Booking.id)
        )
        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None

    # ---------- Query by Relations ----------
    async def get_by_client(self, client_id: uuid.UUID) -> List[Booking]:
        result = await self.session.execute(
            select(Booking).where(Booking.client_id == client_id)
        )
        return result.scalars().all()

    async def get_by_agent(self, agent_id: uuid.UUID) -> List[Booking]:
        result = await self.session.execute(
            select(Booking).where(Booking.agent_id == agent_id)
        )
        return result.scalars().all()

    async def get_by_package(self, package_id: uuid.UUID) -> List[Booking]:
        result = await self.session.execute(
            select(Booking).where(Booking.package_id == package_id)
        )
        return result.scalars().all()

    async def get_by_status(self, status: BookingStatusEnum) -> List[Booking]:
        result = await self.session.execute(
            select(Booking).where(Booking.status == status)
        )
        return result.scalars().all()

    async def get_by_country(self, country: CountryEnum) -> List[Booking]:
        result = await self.session.execute(
            select(Booking).where(Booking.travelling_from == country)
        )
        return result.scalars().all()

    # ---------- Updates ----------
    async def update_status(
        self, booking_id: uuid.UUID, new_status: BookingStatusEnum
    ) -> Optional[Booking]:
        await self.session.execute(
            update(Booking).where(Booking.id == booking_id).values(status=new_status)
        )
        await self.session.flush()
        return await self.get_by_id(booking_id)

    async def assign_agent(
        self, booking_id: uuid.UUID, agent_id: uuid.UUID
    ) -> Optional[Booking]:
        await self.session.execute(
            update(Booking).where(Booking.id == booking_id).values(agent_id=agent_id)
        )
        await self.session.flush()
        return await self.get_by_id(booking_id)

    async def move_booking(
        self, booking_id: uuid.UUID, new_booking_id: uuid.UUID
    ) -> Optional[Booking]:
        """Link this booking to another (moved_to_booking_id)."""
        await self.session.execute(
            update(Booking)
            .where(Booking.id == booking_id)
            .values(moved_to_booking_id=new_booking_id)
        )
        await self.session.flush()
        return await self.get_by_id(booking_id)

    # ---------- Business Queries ----------
    async def get_active_bookings(self) -> List[Booking]:
        """Bookings that are not cancelled or completed."""
        result = await self.session.execute(
            select(Booking).where(
                Booking.status.not_in(
                    [
                        BookingStatusEnum.CANCELLED,
                        BookingStatusEnum.COMPLETED,
                    ]
                )
            )
        )
        return result.scalars().all()

    async def get_moved_bookings(self, original_booking_id: uuid.UUID) -> List[Booking]:
        """Get all bookings moved from a given booking id."""
        result = await self.session.execute(
            select(Booking).where(Booking.moved_to_booking_id == original_booking_id)
        )
        return result.scalars().all()
