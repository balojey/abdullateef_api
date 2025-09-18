import uuid
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.dependencies import get_db_session
from abdullateef_api.db.enums import CommissionStatusEnum
from abdullateef_api.db.models.commission import Commission


class CommissionDAO:
    """Data Access Object for commissions table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    # -------------------------------
    # Create
    # -------------------------------
    async def create(
        self,
        agent_id: uuid.UUID,
        booking_id: uuid.UUID,
        commission_amount: int,
        status: CommissionStatusEnum = CommissionStatusEnum.PENDING,
    ) -> Commission:
        """
        Create a new commission entry.

        :param agent_id: UUID of the agent.
        :param booking_id: UUID of the booking.
        :param commission_amount: Amount of commission.
        :param status: Commission status.
        :return: Created Commission object.
        """
        commission = Commission(
            agent_id=agent_id,
            booking_id=booking_id,
            commission_amount=commission_amount,
            status=status,
        )
        self.session.add(commission)
        await self.session.flush()
        return commission

    # -------------------------------
    # Read
    # -------------------------------
    async def get_by_id(self, commission_id: uuid.UUID) -> Optional[Commission]:
        """Get commission by ID."""
        result = await self.session.execute(
            select(Commission).where(Commission.id == commission_id),
        )
        return result.scalar_one_or_none()

    async def get_by_agent(self, agent_id: uuid.UUID) -> List[Commission]:
        """Get all commissions for a given agent."""
        result = await self.session.execute(
            select(Commission).where(Commission.agent_id == agent_id),
        )
        return list(result.scalars().fetchall())

    async def get_by_booking(self, booking_id: uuid.UUID) -> List[Commission]:
        """Get all commissions for a given booking."""
        result = await self.session.execute(
            select(Commission).where(Commission.booking_id == booking_id),
        )
        return list(result.scalars().fetchall())

    async def get_by_status(
        self,
        status: CommissionStatusEnum,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Commission]:
        """Get commissions by status with pagination."""
        result = await self.session.execute(
            select(Commission)
            .where(Commission.status == status)
            .limit(limit)
            .offset(offset),
        )
        return list(result.scalars().fetchall())

    async def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Commission]:
        """List all commissions with pagination."""
        result = await self.session.execute(
            select(Commission).limit(limit).offset(offset),
        )
        return list(result.scalars().fetchall())

    # -------------------------------
    # Update
    # -------------------------------
    async def update_status(
        self,
        commission_id: uuid.UUID,
        new_status: CommissionStatusEnum,
    ) -> Optional[Commission]:
        """
        Update the status of a commission.
        """
        await self.session.execute(
            update(Commission)
            .where(Commission.id == commission_id)
            .values(status=new_status),
        )
        return await self.get_by_id(commission_id)

    async def update_amount(
        self,
        commission_id: uuid.UUID,
        new_amount: int,
    ) -> Optional[Commission]:
        """
        Update the commission amount.
        """
        await self.session.execute(
            update(Commission)
            .where(Commission.id == commission_id)
            .values(commission_amount=new_amount),
        )
        return await self.get_by_id(commission_id)

    # -------------------------------
    # Delete
    # -------------------------------
    async def delete(self, commission_id: uuid.UUID) -> bool:
        """Delete a commission by ID."""
        result = await self.session.execute(
            delete(Commission).where(Commission.id == commission_id),
        )
        return result.rowcount > 0
