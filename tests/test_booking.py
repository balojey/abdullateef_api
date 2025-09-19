import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.dao.booking_dao import BookingDAO
from abdullateef_api.db.enums import BookingStatusEnum, CountryEnum
from abdullateef_api.db.models.agent import Agent
from abdullateef_api.db.models.client import Client
from abdullateef_api.db.models.hajj_package import HajjPackage


# ---------- Helper factories ----------
async def create_agent(session: AsyncSession, agent_code: str | None = None) -> Agent:
    agent = Agent(
        id=uuid.uuid4(),
        first_name="AgentFirst",
        last_name="AgentLast",
        agent_code=agent_code or uuid.uuid4().hex[:5].upper(),
        phone_number="08000000000",
    )
    session.add(agent)
    await session.flush()
    return agent


async def create_package(
    session: AsyncSession, year: int = 2030, commission_amount: int = 1000,
) -> HajjPackage:
    package = HajjPackage(
        id=uuid.uuid4(),
        year=year,
        local_price=1_000_000,
        diaspora_price=1_500_000,
        registration_fee=50_000,
        commission_amount=commission_amount,
    )
    session.add(package)
    await session.flush()
    return package


async def create_client(
    session: AsyncSession,
    referee_id: uuid.UUID | None = None,
    passport: str | None = None,
) -> Client:
    client = Client(
        id=uuid.uuid4(),
        first_name="ClientFirst",
        last_name="ClientLast",
        sex="MALE",
        phone_number="08011112222",
        passport_number=passport or uuid.uuid4().hex[:8],
        location=CountryEnum.NG,
        referee_id=referee_id,
    )
    session.add(client)
    await session.flush()
    return client


@pytest.mark.anyio
class TestBookingDAO:
    async def test_create_and_get_by_id(self, dbsession: AsyncSession) -> None:
        dao = BookingDAO(dbsession)

        agent = await create_agent(dbsession)
        package = await create_package(dbsession)
        client = await create_client(dbsession, referee_id=agent.id)

        booking = await dao.create(
            client_id=client.id,
            package_id=package.id,
            agent_id=agent.id,
            travelling_from=CountryEnum.NG,
            status=BookingStatusEnum.REGISTERED,
        )
        await dbsession.commit()

        fetched = await dao.get_by_id(booking.id)
        assert fetched is not None
        assert fetched.client_id == client.id
        assert fetched.agent_id == agent.id

    async def test_list_all_and_get_by_package(self, dbsession: AsyncSession) -> None:
        dao = BookingDAO(dbsession)

        package_a = await create_package(dbsession, year=2031)
        package_b = await create_package(dbsession, year=2032)
        client1 = await create_client(dbsession)
        client2 = await create_client(dbsession)

        b1 = await dao.create(client_id=client1.id, package_id=package_a.id)
        b2 = await dao.create(client_id=client2.id, package_id=package_b.id)
        await dbsession.commit()

        all_bookings = await dao.list_all()
        assert any(b.id == b1.id for b in all_bookings)
        assert any(b.id == b2.id for b in all_bookings)

        by_package_a = await dao.get_by_package(package_a.id)
        assert any(b.package_id == package_a.id for b in by_package_a)

    async def test_get_by_client_and_agent(self, dbsession: AsyncSession) -> None:
        dao = BookingDAO(dbsession)

        agent = await create_agent(dbsession)
        package = await create_package(dbsession)
        client = await create_client(dbsession)

        booking = await dao.create(
            client_id=client.id, package_id=package.id, agent_id=agent.id,
        )
        await dbsession.commit()

        client_bookings = await dao.get_by_client(client.id)
        assert any(b.id == booking.id for b in client_bookings)

        agent_bookings = await dao.get_by_agent(agent.id)
        assert any(b.id == booking.id for b in agent_bookings)

    async def test_get_by_status_and_country(self, dbsession: AsyncSession) -> None:
        dao = BookingDAO(dbsession)

        package = await create_package(dbsession)
        client = await create_client(dbsession)

        b1 = await dao.create(
            client_id=client.id,
            package_id=package.id,
            status=BookingStatusEnum.REGISTERED,
            travelling_from=CountryEnum.NG,
        )
        b2 = await dao.create(
            client_id=client.id,
            package_id=package.id,
            status=BookingStatusEnum.COMPLETED,
            travelling_from=CountryEnum.UK,
        )
        await dbsession.commit()

        by_status = await dao.get_by_status(BookingStatusEnum.REGISTERED)
        assert any(b.id == b1.id for b in by_status)

        by_country = await dao.get_by_country(CountryEnum.UK)
        assert any(b.id == b2.id for b in by_country)

    async def test_update_status_assign_and_move(self, dbsession: AsyncSession) -> None:
        dao = BookingDAO(dbsession)

        package = await create_package(dbsession)
        client = await create_client(dbsession)
        agent1 = await create_agent(dbsession, agent_code="AG111")
        agent2 = await create_agent(dbsession, agent_code="AG222")

        booking_a = await dao.create(
            client_id=client.id, package_id=package.id, agent_id=agent1.id,
        )
        booking_b = await dao.create(client_id=client.id, package_id=package.id)
        await dbsession.commit()

        updated = await dao.update_status(booking_a.id, BookingStatusEnum.COMPLETED)
        assert updated.status == BookingStatusEnum.COMPLETED

        assigned = await dao.assign_agent(booking_b.id, agent2.id)
        assert assigned.agent_id == agent2.id

        moved = await dao.move_booking(booking_a.id, booking_b.id)
        assert moved.moved_to_booking_id == booking_b.id

        moved_list = await dao.get_moved_bookings(booking_b.id)
        assert any(b.id == booking_a.id for b in moved_list)

    async def test_get_active_bookings(self, dbsession: AsyncSession) -> None:
        dao = BookingDAO(dbsession)

        package = await create_package(dbsession)
        client = await create_client(dbsession)

        reg = await dao.create(
            client_id=client.id,
            package_id=package.id,
            status=BookingStatusEnum.REGISTERED,
        )
        comp = await dao.create(
            client_id=client.id,
            package_id=package.id,
            status=BookingStatusEnum.COMPLETED,
        )
        await dbsession.commit()

        active = await dao.get_active_bookings()
        assert any(b.id == reg.id for b in active)
        assert all(b.status != BookingStatusEnum.COMPLETED for b in active)

    async def test_delete_and_nonexistent_delete(self, dbsession: AsyncSession) -> None:
        dao = BookingDAO(dbsession)

        package = await create_package(dbsession)
        client = await create_client(dbsession)
        booking = await dao.create(client_id=client.id, package_id=package.id)
        await dbsession.commit()

        deleted = await dao.delete(booking.id)
        assert deleted is True
        assert await dao.get_by_id(booking.id) is None

        deleted_again = await dao.delete(uuid.uuid4())
        assert deleted_again is False

    async def test_get_by_id_nonexistent(self, dbsession: AsyncSession) -> None:
        dao = BookingDAO(dbsession)
        assert await dao.get_by_id(uuid.uuid4()) is None
