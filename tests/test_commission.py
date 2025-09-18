import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.dao.commission_dao import CommissionDAO
from abdullateef_api.db.dao.agent_dao import AgentDAO
from abdullateef_api.db.dao.booking_dao import BookingDAO
from abdullateef_api.db.dao.hajj_package_dao import HajjPackageDAO
from abdullateef_api.db.dao.client_dao import ClientDAO
from abdullateef_api.db.enums import CommissionStatusEnum, GenderEnum, CountryEnum
from abdullateef_api.db.models.commission import Commission


@pytest.mark.anyio
class TestCommissionDAO:
    async def _setup_dependencies(self, dbsession: AsyncSession):
        """Helper to create agent, client, package, booking needed for commissions."""
        agent_dao = AgentDAO(dbsession)
        client_dao = ClientDAO(dbsession)
        package_dao = HajjPackageDAO(dbsession)
        booking_dao = BookingDAO(dbsession)

        # create agent
        agent = await agent_dao.create(
            first_name="Ali",
            last_name="Hassan",
            phone_number="1234567890",
        )

        # create client
        client = await client_dao.create(
            first_name="Omar",
            last_name="Khalid",
            sex=GenderEnum.MALE,
            phone_number="+2348012345678",
            passport_number="PASS123456",
            location=CountryEnum.NG,
            referee_id=agent.id,
        )

        # create package
        package = await package_dao.create(
            year=2025,
            local_price=500000,
            diaspora_price=800000,
            registration_fee=20000,
            commission_amount=50000,
        )

        # create booking
        booking = await booking_dao.create(
            client_id=client.id,
            package_id=package.id,
            agent_id=agent.id,
        )

        return agent, booking

    async def test_create_and_get_by_id(self, dbsession: AsyncSession):
        dao = CommissionDAO(dbsession)
        agent, booking = await self._setup_dependencies(dbsession)

        commission = await dao.create(
            agent_id=agent.id,
            booking_id=booking.id,
            commission_amount=50000,
        )

        fetched = await dao.get_by_id(commission.id)
        assert fetched is not None
        assert fetched.agent_id == agent.id
        assert fetched.booking_id == booking.id
        assert fetched.commission_amount == 50000
        assert fetched.status == CommissionStatusEnum.PENDING

    async def test_get_by_agent_and_booking(self, dbsession: AsyncSession):
        dao = CommissionDAO(dbsession)
        agent, booking = await self._setup_dependencies(dbsession)

        commission = await dao.create(
            agent_id=agent.id,
            booking_id=booking.id,
            commission_amount=60000,
        )

        by_agent = await dao.get_by_agent(agent.id)
        assert commission.id in [c.id for c in by_agent]

        by_booking = await dao.get_by_booking(booking.id)
        assert commission.id in [c.id for c in by_booking]

    async def test_get_by_status_and_list_all(self, dbsession: AsyncSession):
        dao = CommissionDAO(dbsession)
        agent, booking = await self._setup_dependencies(dbsession)

        commission1 = await dao.create(
            agent_id=agent.id,
            booking_id=booking.id,
            commission_amount=70000,
            status=CommissionStatusEnum.PENDING,
        )
        commission2 = await dao.create(
            agent_id=agent.id,
            booking_id=booking.id,
            commission_amount=80000,
            status=CommissionStatusEnum.PAID,
        )

        pending = await dao.get_by_status(CommissionStatusEnum.PENDING)
        paid = await dao.get_by_status(CommissionStatusEnum.PAID)

        assert commission1.id in [c.id for c in pending]
        assert commission2.id in [c.id for c in paid]

        all_commissions = await dao.list_all()
        assert len(all_commissions) >= 2

    async def test_update_status_and_amount(self, dbsession: AsyncSession):
        dao = CommissionDAO(dbsession)
        agent, booking = await self._setup_dependencies(dbsession)

        commission = await dao.create(
            agent_id=agent.id,
            booking_id=booking.id,
            commission_amount=90000,
        )

        # update status
        updated_status = await dao.update_status(
            commission.id, CommissionStatusEnum.PAID
        )
        assert updated_status.status == CommissionStatusEnum.PAID

        # update amount
        updated_amount = await dao.update_amount(commission.id, 120000)
        assert updated_amount.commission_amount == 120000

    async def test_delete(self, dbsession: AsyncSession):
        dao = CommissionDAO(dbsession)
        agent, booking = await self._setup_dependencies(dbsession)

        commission = await dao.create(
            agent_id=agent.id,
            booking_id=booking.id,
            commission_amount=100000,
        )

        deleted = await dao.delete(commission.id)
        assert deleted is True

        should_be_none = await dao.get_by_id(commission.id)
        assert should_be_none is None
