import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.dao.agent_dao import AgentDAO
from abdullateef_api.db.models.booking import Booking
from abdullateef_api.db.models.commission import Commission
from abdullateef_api.db.models.client import Client
from abdullateef_api.db.models.hajj_package import HajjPackage


@pytest.mark.anyio
async def test_create_agent_without_code(dbsession: AsyncSession) -> None:
    """Agent should be created with an auto-generated code if not supplied."""
    dao = AgentDAO(dbsession)

    agent = await dao.create_agent(
        first_name="John",
        last_name="Doe",
        phone_number="12345",
    )

    assert isinstance(agent.id, uuid.UUID)
    assert len(agent.agent_code) == 5
    assert any(c.isdigit() for c in agent.agent_code)
    assert any(c.isalpha() for c in agent.agent_code)


@pytest.mark.anyio
async def test_create_agent_with_code(dbsession: AsyncSession) -> None:
    """Agent should be created with a provided custom code."""
    dao = AgentDAO(dbsession)

    custom_code = "AB123"
    agent = await dao.create_agent(
        first_name="Jane",
        last_name="Smith",
        phone_number="67890",
        agent_code=custom_code,
    )

    assert agent.agent_code == custom_code


@pytest.mark.anyio
async def test_get_by_id_and_code(dbsession: AsyncSession) -> None:
    """Agents should be retrievable by ID and code."""
    dao = AgentDAO(dbsession)

    agent = await dao.create_agent(first_name="Alice", last_name="Brown")
    fetched_by_id = await dao.get_by_id(agent.id)
    fetched_by_code = await dao.get_by_code(agent.agent_code)

    assert fetched_by_id.id == agent.id
    assert fetched_by_code.agent_code == agent.agent_code


@pytest.mark.anyio
async def test_get_by_phone(dbsession: AsyncSession) -> None:
    """Agents should be retrievable by phone number."""
    dao = AgentDAO(dbsession)
    phone = "555123"

    agent = await dao.create_agent(
        first_name="Phone",
        last_name="Test",
        phone_number=phone,
    )

    fetched = await dao.get_by_phone(phone)
    assert fetched is not None
    assert fetched.phone_number == phone


@pytest.mark.anyio
async def test_filter_by_name(dbsession: AsyncSession) -> None:
    """Agents can be filtered by partial name matches."""
    dao = AgentDAO(dbsession)

    await dao.create_agent(first_name="Filter", last_name="Target")
    results = await dao.filter_by_name(first_name="Fil")

    assert len(results) == 1
    assert results[0].first_name == "Filter"


@pytest.mark.anyio
async def test_list_agents(dbsession: AsyncSession) -> None:
    """List multiple agents with pagination."""
    dao = AgentDAO(dbsession)

    await dao.create_agent(first_name="A1", last_name="Test")
    await dao.create_agent(first_name="A2", last_name="Test")
    agents = await dao.list_agents(limit=10, offset=0)

    assert len(agents) >= 2


@pytest.mark.anyio
async def test_update_agent(dbsession: AsyncSession) -> None:
    """Agent details should be updatable."""
    dao = AgentDAO(dbsession)

    agent = await dao.create_agent(first_name="Old", last_name="Name")
    updated = await dao.update_agent(agent.id, first_name="New")

    assert updated.first_name == "New"


@pytest.mark.anyio
async def test_regenerate_agent_code(dbsession: AsyncSession) -> None:
    """Agent code should change when regenerated."""
    dao = AgentDAO(dbsession)

    agent = await dao.create_agent(first_name="Code", last_name="Changer")
    old_code = agent.agent_code

    updated = await dao.regenerate_agent_code(agent.id)
    assert updated.agent_code != old_code
    assert len(updated.agent_code) == 5


@pytest.mark.anyio
async def test_delete_agent(dbsession: AsyncSession) -> None:
    """Agents should be deletable."""
    dao = AgentDAO(dbsession)

    agent = await dao.create_agent(first_name="Delete", last_name="Me")
    await dao.delete_agent(agent.id)

    deleted = await dao.get_by_id(agent.id)
    assert deleted is None


@pytest.mark.anyio
async def test_relationship_helpers(dbsession: AsyncSession) -> None:
    """Check relationship fetching for bookings, commissions, and clients."""
    dao = AgentDAO(dbsession)

    agent = await dao.create_agent(first_name="Rel", last_name="Test")

    # manually insert related records
    hajj_package = HajjPackage(id=uuid.uuid4(), year=2028, local_price=10000000, diaspora_price=9000000, registration_fee=20000, commission_amount=700000)
    client = Client(id=uuid.uuid4(), first_name="Ref", last_name="Client", referee_id=agent.id, passport_number="P123456", location="NG", sex="MALE", phone_number="0383932028393")
    booking = Booking(id=uuid.uuid4(), agent_id=agent.id, client_id=client.id, package_id=hajj_package.id, status="REGISTERED")
    commission = Commission(id=uuid.uuid4(), agent_id=agent.id, booking_id=booking.id, commission_amount=hajj_package.commission_amount)

    dbsession.add_all([hajj_package, booking, commission, client])
    await dbsession.flush()

    bookings = await dao.get_bookings(agent.id)
    commissions = await dao.get_commissions(agent.id)
    referred = await dao.get_referred_clients(agent.id)

    assert len(bookings) == 1
    assert len(commissions) == 1
    assert len(referred) == 1
