from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.dao.agent_dao import AgentDAO
from abdullateef_api.db.dao.booking_dao import BookingDAO
from abdullateef_api.db.dao.client_dao import ClientDAO
from abdullateef_api.db.dao.hajj_package_dao import HajjPackageDAO
from abdullateef_api.db.dao.payment_transaction_dao import PaymentTransactionDAO
from abdullateef_api.db.enums import CountryEnum, GenderEnum, PaymentTypeEnum
from abdullateef_api.db.models.payment_transaction import PaymentTransaction


@pytest.mark.anyio
class TestPaymentTransactionDAO:
    async def _create_dependencies(self, dbsession: AsyncSession):
        """Helper to create an agent, client, and booking for payment transactions."""
        agent_dao = AgentDAO(dbsession)
        client_dao = ClientDAO(dbsession)
        booking_dao = BookingDAO(dbsession)
        hajj_package_dao = HajjPackageDAO(dbsession)

        # Create agent
        agent = await agent_dao.create_agent(
            first_name="James",
            last_name="Bond",
            phone_number="+2348011122233",
        )

        # Create client
        client = await client_dao.create_client(
            first_name="Jane",
            last_name="Smith",
            sex=GenderEnum.FEMALE,
            phone_number="+2348098765432",
            passport_number="B98765432",
            date_of_birth=date(1992, 8, 15),
            location=CountryEnum.NG,
            referee_id=agent.id,
        )

        # Create hajj package
        hajj_package = await hajj_package_dao.create_hajj_package(
            year=2028,
            local_price=10000000,
            diaspora_price=9000000,
            registration_fee=20000,
            commission_amount=700000,
        )

        # Create booking
        booking = await booking_dao.create(
            client_id=client.id,
            agent_id=agent.id,
            travelling_from=CountryEnum.UK,
            package_id=hajj_package.id,
        )

        return booking

    async def test_create_and_get_by_id(self, dbsession: AsyncSession):
        """Test creating a payment transaction and fetching by ID."""
        booking = await self._create_dependencies(dbsession)
        dao = PaymentTransactionDAO(dbsession)

        tx = await dao.create_payment_transaction(
            booking_id=booking.id,
            amount=50000,
            payment_type=PaymentTypeEnum.REGISTRATION,
        )

        fetched = await dao.get_by_id(tx.id)
        assert fetched is not None
        assert fetched.amount == 50000
        assert fetched.payment_type == PaymentTypeEnum.REGISTRATION

    async def test_get_by_booking_id(self, dbsession: AsyncSession):
        """Test fetching transactions by booking_id."""
        booking = await self._create_dependencies(dbsession)
        dao = PaymentTransactionDAO(dbsession)

        tx1 = await dao.create_payment_transaction(
            booking.id, 20000, PaymentTypeEnum.REGISTRATION,
        )
        tx2 = await dao.create_payment_transaction(
            booking.id, 30000, PaymentTypeEnum.INSTALLMENT,
        )

        transactions = await dao.get_by_booking_id(booking.id)
        assert len(transactions) == 2
        assert {t.amount for t in transactions} == {20000, 30000}

    async def test_get_by_payment_type(self, dbsession: AsyncSession):
        """Test fetching transactions by payment type."""
        booking = await self._create_dependencies(dbsession)
        dao = PaymentTransactionDAO(dbsession)

        await dao.create_payment_transaction(
            booking.id, 40000, PaymentTypeEnum.REGISTRATION,
        )
        await dao.create_payment_transaction(
            booking.id, 25000, PaymentTypeEnum.INSTALLMENT,
        )

        card_payments = await dao.get_by_payment_type(PaymentTypeEnum.REGISTRATION)
        assert len(card_payments) >= 1
        assert all(
            tx.payment_type == PaymentTypeEnum.REGISTRATION for tx in card_payments
        )

    async def test_list_all(self, dbsession: AsyncSession):
        """Test fetching all transactions."""
        booking = await self._create_dependencies(dbsession)
        dao = PaymentTransactionDAO(dbsession)

        await dao.create_payment_transaction(
            booking.id, 10000, PaymentTypeEnum.INSTALLMENT,
        )
        await dao.create_payment_transaction(
            booking.id, 15000, PaymentTypeEnum.REGISTRATION,
        )

        all_tx = await dao.list_all()
        assert len(all_tx) >= 2
        assert isinstance(all_tx[0], PaymentTransaction)

    async def test_update_transaction_amount(self, dbsession: AsyncSession):
        """Test updating the amount of a transaction."""
        booking = await self._create_dependencies(dbsession)
        dao = PaymentTransactionDAO(dbsession)

        tx = await dao.create_payment_transaction(
            booking.id, 7000, PaymentTypeEnum.INSTALLMENT,
        )
        updated = await dao.update_transaction_amount(tx.id, 9000)

        assert updated is not None
        assert updated.amount == 9000

    async def test_update_payment_type(self, dbsession: AsyncSession):
        """Test updating the payment type of a transaction."""
        booking = await self._create_dependencies(dbsession)
        dao = PaymentTransactionDAO(dbsession)

        tx = await dao.create_payment_transaction(
            booking.id, 12000, PaymentTypeEnum.INSTALLMENT,
        )
        updated = await dao.update_payment_type(tx.id, PaymentTypeEnum.REGISTRATION)

        assert updated is not None
        assert updated.payment_type == PaymentTypeEnum.REGISTRATION

    async def test_delete_transaction(self, dbsession: AsyncSession):
        """Test deleting a transaction."""
        booking = await self._create_dependencies(dbsession)
        dao = PaymentTransactionDAO(dbsession)

        tx = await dao.create_payment_transaction(
            booking.id, 15000, PaymentTypeEnum.INSTALLMENT,
        )
        await dao.delete_transaction(tx.id)

        fetched = await dao.get_by_id(tx.id)
        assert fetched is None
