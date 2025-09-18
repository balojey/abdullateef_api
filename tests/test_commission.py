import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.dao.commission_dao import CommissionDAO
from abdullateef_api.db.enums import CommissionStatusEnum
from abdullateef_api.db.models.commission import Commission
from abdullateef_api.db.models.agent import Agent
from abdullateef_api.db.models.booking import Booking
from abdullateef_api.db.models.client import Client
from abdullateef_api.db.models.hajj_package import HajjPackage


# ---------- Fixtures & Factories ----------

@pytest.fixture
def agent_factory():
    def _create_agent(agent_code="AG123"):
        return Agent(
            id=uuid.uuid4(),
            first_name="Ali",
            last_name="Hassan",
            agent_code=agent_code,
        )
    return _create_agent


@pytest.fixture
def package_factory():
    def _create_package(year=2028, commission_amount=700000):
        return HajjPackage(
            id=uuid.uuid4(),
            year=year,
            local_price=10000000,
            diaspora_price=9000000,
            registration_fee=20000,
            commission_amount=commission_amount,
        )
    return _create_package


@pytest.fixture
def client_factory():
    def _create_client(agent_id, passport_number="P123456"):
        return Client(
            id=uuid.uuid4(),
            first_name="Ref",
            last_name="Client",
            referee_id=agent_id,
            passport_number=passport_number,
            location="NG",
            sex="MALE",
            phone_number="0383932028393",
        )
    return _create_client


@pytest.fixture
def booking_factory():
    def _create_booking(client_id, package_id):
        return Booking(
            id=uuid.uuid4(),
            client_id=client_id,
            package_id=package_id,
        )
    return _create_booking


@pytest.fixture
def commission_factory():
    def _create_commission(agent_id, booking_id, amount, status=CommissionStatusEnum.PENDING):
        return Commission(
            agent_id=agent_id,
            booking_id=booking_id,
            commission_amount=amount,
            status=status,
        )
    return _create_commission


# ---------- Tests ----------

@pytest.mark.anyio
async def test_create_and_get_by_id(
    dbsession: AsyncSession,
    agent_factory,
    package_factory,
    client_factory,
    booking_factory,
    commission_factory,
) -> None:
    """Test commission creation and retrieval by id."""
    dao = CommissionDAO(dbsession)

    agent = agent_factory()
    package = package_factory()
    client = client_factory(agent.id)
    booking = booking_factory(client.id, package.id)
    dbsession.add_all([agent, package, client, booking])
    await dbsession.flush()

    commission = await dao.create(
        agent_id=agent.id,
        booking_id=booking.id,
        commission_amount=500,
    )
    await dbsession.commit()

    found = await dao.get_by_id(commission.id)
    assert found is not None
    assert found.agent_id == agent.id
    assert found.booking_id == booking.id
    assert found.commission_amount == 500
    assert found.status == CommissionStatusEnum.PENDING


@pytest.mark.anyio
async def test_get_by_agent_and_booking(
    dbsession: AsyncSession,
    agent_factory,
    package_factory,
    client_factory,
    booking_factory,
    commission_factory,
) -> None:
    """Test retrieval by agent_id and booking_id."""
    dao = CommissionDAO(dbsession)

    agent = agent_factory()
    package = package_factory()
    client = client_factory(agent.id)
    booking = booking_factory(client.id, package.id)
    commission = commission_factory(agent.id, booking.id, package.commission_amount)

    dbsession.add_all([agent, package, client, booking, commission])
    await dbsession.commit()

    by_agent = await dao.get_by_agent(agent.id)
    assert len(by_agent) == 1
    assert by_agent[0].commission_amount == package.commission_amount

    by_booking = await dao.get_by_booking(booking.id)
    assert len(by_booking) == 1
    assert by_booking[0].id == commission.id


@pytest.mark.anyio
async def test_get_by_status_and_list_all(
    dbsession: AsyncSession,
    agent_factory,
    package_factory,
    client_factory,
    booking_factory,
    commission_factory,
) -> None:
    """Test retrieval by status and list_all."""
    dao = CommissionDAO(dbsession)

    agent1 = agent_factory("AG123")
    package1 = package_factory(2028, 700000)
    client1 = client_factory(agent1.id, "P123456")
    booking1 = booking_factory(client1.id, package1.id)
    commission1 = commission_factory(agent1.id, booking1.id, package1.commission_amount)

    agent2 = agent_factory("AG124")
    package2 = package_factory(2029, 700000)
    client2 = client_factory(agent2.id, "P123457")
    booking2 = booking_factory(client2.id, package2.id)
    commission2 = commission_factory(agent2.id, booking2.id, package2.commission_amount, status=CommissionStatusEnum.PAID)

    dbsession.add_all([agent1, package1, client1, booking1, commission1,
                       agent2, package2, client2, booking2, commission2])
    await dbsession.commit()

    pending = await dao.get_by_status(CommissionStatusEnum.PENDING)
    assert any(c.id == commission1.id for c in pending)

    paid = await dao.get_by_status(CommissionStatusEnum.PAID)
    assert any(c.id == commission2.id for c in paid)

    all_commissions = await dao.list_all()
    assert len(all_commissions) >= 2


@pytest.mark.anyio
async def test_update_status_and_amount(
    dbsession: AsyncSession,
    agent_factory,
    package_factory,
    client_factory,
    booking_factory,
    commission_factory,
) -> None:
    """Test updating commission status and amount."""
    dao = CommissionDAO(dbsession)

    agent = agent_factory()
    package = package_factory()
    client = client_factory(agent.id)
    booking = booking_factory(client.id, package.id)
    commission = commission_factory(agent.id, booking.id, package.commission_amount)

    dbsession.add_all([agent, package, client, booking, commission])
    await dbsession.commit()

    updated_status = await dao.update_status(commission.id, CommissionStatusEnum.PAID)
    assert updated_status.status == CommissionStatusEnum.PAID

    updated_amount = await dao.update_amount(commission.id, 999)
    assert updated_amount.commission_amount == 999


@pytest.mark.anyio
async def test_delete_commission(
    dbsession: AsyncSession,
    agent_factory,
    package_factory,
    client_factory,
    booking_factory,
    commission_factory,
) -> None:
    """Test deleting a commission by ID."""
    dao = CommissionDAO(dbsession)

    agent = agent_factory()
    package = package_factory()
    client = client_factory(agent.id)
    booking = booking_factory(client.id, package.id)
    commission = commission_factory(agent.id, booking.id, package.commission_amount)

    dbsession.add_all([agent, package, client, booking, commission])
    await dbsession.commit()

    deleted = await dao.delete(commission.id)
    assert deleted is True

    missing = await dao.get_by_id(commission.id)
    assert missing is None
