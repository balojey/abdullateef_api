import uuid
from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.enums import PaymentTypeEnum
from abdullateef_api.db.models.payment_transaction import PaymentTransaction


class PaymentTransactionDAO:
    """DAO for PaymentTransaction model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------
    # CREATE
    # ------------------------------
    async def create_payment_transaction(
        self,
        booking_id: uuid.UUID,
        amount: int,
        payment_type: PaymentTypeEnum,
    ) -> PaymentTransaction:
        """Create a new payment transaction."""
        transaction = PaymentTransaction(
            booking_id=booking_id,
            amount=amount,
            payment_type=payment_type,
        )
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    # ------------------------------
    # READ
    # ------------------------------
    async def get_by_id(
        self, transaction_id: uuid.UUID,
    ) -> Optional[PaymentTransaction]:
        """Fetch a payment transaction by ID."""
        result = await self.session.execute(
            select(PaymentTransaction).where(PaymentTransaction.id == transaction_id),
        )
        return result.scalar_one_or_none()

    async def get_by_booking_id(
        self, booking_id: uuid.UUID,
    ) -> List[PaymentTransaction]:
        """Fetch all payment transactions for a given booking."""
        result = await self.session.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.booking_id == booking_id,
            ),
        )
        return list(result.scalars().all())

    async def get_by_payment_type(
        self, payment_type: PaymentTypeEnum,
    ) -> List[PaymentTransaction]:
        """Fetch all transactions of a given payment type."""
        result = await self.session.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.payment_type == payment_type,
            ),
        )
        return list(result.scalars().all())

    async def list_all(self) -> List[PaymentTransaction]:
        """Fetch all payment transactions."""
        result = await self.session.execute(select(PaymentTransaction))
        return list(result.scalars().all())

    # ------------------------------
    # UPDATE
    # ------------------------------
    async def update_transaction_amount(
        self,
        transaction_id: uuid.UUID,
        new_amount: int,
    ) -> Optional[PaymentTransaction]:
        """Update the amount of a payment transaction."""
        await self.session.execute(
            update(PaymentTransaction)
            .where(PaymentTransaction.id == transaction_id)
            .values(amount=new_amount),
        )
        await self.session.flush()
        return await self.get_by_id(transaction_id)

    async def update_payment_type(
        self,
        transaction_id: uuid.UUID,
        new_type: PaymentTypeEnum,
    ) -> Optional[PaymentTransaction]:
        """Update the payment type of a transaction."""
        await self.session.execute(
            update(PaymentTransaction)
            .where(PaymentTransaction.id == transaction_id)
            .values(payment_type=new_type),
        )
        await self.session.flush()
        return await self.get_by_id(transaction_id)

    # ------------------------------
    # DELETE
    # ------------------------------
    async def delete_transaction(self, transaction_id: uuid.UUID) -> None:
        """Delete a transaction by ID."""
        await self.session.execute(
            delete(PaymentTransaction).where(PaymentTransaction.id == transaction_id),
        )
        await self.session.flush()
