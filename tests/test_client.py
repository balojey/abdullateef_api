from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.dao.agent_dao import AgentDAO
from abdullateef_api.db.dao.client_dao import ClientDAO
from abdullateef_api.db.enums import CountryEnum, GenderEnum


@pytest.mark.anyio
class TestClientDAO:
    async def test_create_and_get_by_id(self, dbsession: AsyncSession) -> None:
        """Test client creation and retrieval by ID."""
        dao = ClientDAO(dbsession)

        client = await dao.create_client(
            first_name="John",
            last_name="Doe",
            sex=GenderEnum.MALE,
            phone_number="+2348012345678",
            passport_number="A12345678",
            date_of_birth=date(1990, 5, 20),
            location=CountryEnum.NG,
        )

        fetched = await dao.get_by_id(client.id)
        assert fetched is not None
        assert fetched.first_name == "John"
        assert fetched.passport_number == "A12345678"

    async def test_get_by_passport_number(self, dbsession: AsyncSession) -> None:
        """Test retrieval of client by passport number."""
        dao = ClientDAO(dbsession)

        passport_number = "B87654321"
        await dao.create_client(
            first_name="Jane",
            last_name="Smith",
            sex=GenderEnum.FEMALE,
            phone_number="+2348098765432",
            passport_number=passport_number,
            location=CountryEnum.NG,
        )

        fetched = await dao.get_by_passport(passport_number)
        assert fetched is not None
        assert fetched.last_name == "Smith"

    async def test_get_by_name(self, dbsession: AsyncSession) -> None:
        """Test retrieval of clients by name (case-insensitive)."""
        dao = ClientDAO(dbsession)

        await dao.create_client(
            first_name="Michael",
            last_name="Jordan",
            sex=GenderEnum.MALE,
            phone_number="+2348000111222",
            passport_number="C99887766",
            location=CountryEnum.NG,
        )

        results = await dao.get_by_name("michael")
        assert len(results) == 1
        assert results[0].last_name == "Jordan"

    async def test_get_by_referee_id(self, dbsession: AsyncSession) -> None:
        """Test retrieval of clients by referee_id (UUID)."""
        agent_dao = AgentDAO(dbsession)
        client_dao = ClientDAO(dbsession)

        agent = await agent_dao.create_agent(first_name="Ref", last_name="Eree")
        client = await client_dao.create_client(
            first_name="Ali",
            last_name="Baba",
            sex=GenderEnum.MALE,
            phone_number="+2348112233445",
            passport_number="D12312312",
            location=CountryEnum.NG,
            referee_id=agent.id,
        )

        results = await client_dao.get_by_referee(agent.id)
        assert len(results) == 1
        assert results[0].first_name == "Ali"

    async def test_get_by_referee_code(self, dbsession: AsyncSession) -> None:
        """Test retrieval of clients by referee's agent_code."""
        agent_dao = AgentDAO(dbsession)
        client_dao = ClientDAO(dbsession)

        agent = await agent_dao.create_agent(first_name="Code", last_name="Agent")
        referee_code = agent.agent_code

        await client_dao.create_client(
            first_name="Lara",
            last_name="Croft",
            sex=GenderEnum.FEMALE,
            phone_number="+2348223344556",
            passport_number="E444555666",
            location=CountryEnum.NG,
            referee_id=agent.id,
        )

        results = await client_dao.get_by_referee(referee_code)
        assert len(results) == 1
        assert results[0].first_name == "Lara"

    async def test_update_client(self, dbsession: AsyncSession) -> None:
        """Test updating a client's details."""
        dao = ClientDAO(dbsession)

        client = await dao.create_client(
            first_name="Chris",
            last_name="Evans",
            sex=GenderEnum.MALE,
            phone_number="+2348333444555",
            passport_number="F555666777",
            location=CountryEnum.NG,
        )

        updated = await dao.update_client(
            client.id,
            phone_number="+2348999888777",
            last_name="Pratt",
        )

        assert updated is not None
        assert updated.phone_number == "+2348999888777"
        assert updated.last_name == "Pratt"

    async def test_delete_client(self, dbsession: AsyncSession) -> None:
        """Test deleting a client."""
        dao = ClientDAO(dbsession)

        client = await dao.create_client(
            first_name="Mark",
            last_name="Twain",
            sex=GenderEnum.MALE,
            phone_number="+2348444555666",
            passport_number="G111222333",
            location=CountryEnum.NG,
        )

        result = await dao.delete_client(client.id)
        assert result is True

        fetched = await dao.get_by_id(client.id)
        assert fetched is None
