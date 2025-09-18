import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.dao.note_dao import NoteDAO
from abdullateef_api.db.dao.client_dao import ClientDAO
from abdullateef_api.db.enums import GenderEnum, CountryEnum


@pytest.mark.anyio
class TestNoteDAO:
    async def _create_client(self, dbsession: AsyncSession):
        """Helper to create a client for note tests."""
        client_dao = ClientDAO(dbsession)
        return await client_dao.create_client(
            first_name="Jane",
            last_name="Smith",
            sex=GenderEnum.FEMALE,
            phone_number="+2348011111111",
            passport_number=uuid.uuid4().hex,
            location=CountryEnum.NG,
        )

    async def test_create_and_get_by_id(self, dbsession: AsyncSession):
        """Test creating a note and retrieving it by ID."""
        client = await self._create_client(dbsession)
        dao = NoteDAO(dbsession)

        note = await dao.create_note(client_id=client.id, content="Test note")
        fetched = await dao.get_by_id(note.id)

        assert fetched is not None
        assert fetched.id == note.id
        assert fetched.content == "Test note"

    async def test_get_by_client_id(self, dbsession: AsyncSession):
        """Test retrieving notes by client ID."""
        client = await self._create_client(dbsession)
        dao = NoteDAO(dbsession)

        note1 = await dao.create_note(client_id=client.id, content="Note 1")
        note2 = await dao.create_note(client_id=client.id, content="Note 2")

        notes = await dao.get_by_client_id(client.id)

        assert len(notes) == 2
        assert {n.content for n in notes} == {"Note 1", "Note 2"}
        assert all(n.client_id == client.id for n in notes)

    async def test_get_by_created_by(self, dbsession: AsyncSession):
        """Test retrieving notes created by a specific user."""
        client = await self._create_client(dbsession)
        dao = NoteDAO(dbsession)
        creator_id = uuid.uuid4()

        await dao.create_note(client_id=client.id, content="Creator note", created_by=creator_id)
        await dao.create_note(client_id=client.id, content="Another note", created_by=creator_id)

        notes = await dao.get_by_created_by(creator_id)

        assert len(notes) == 2
        assert all(n.created_by == creator_id for n in notes)

    async def test_list_all(self, dbsession: AsyncSession):
        """Test listing all notes."""
        client = await self._create_client(dbsession)
        dao = NoteDAO(dbsession)

        await dao.create_note(client_id=client.id, content="Note A")
        await dao.create_note(client_id=client.id, content="Note B")

        all_notes = await dao.list_all()

        assert len(all_notes) >= 2
        assert any(n.content == "Note A" for n in all_notes)
        assert any(n.content == "Note B" for n in all_notes)

    async def test_update_content(self, dbsession: AsyncSession):
        """Test updating the content of a note."""
        client = await self._create_client(dbsession)
        dao = NoteDAO(dbsession)

        note = await dao.create_note(client_id=client.id, content="Old content")
        updated = await dao.update_content(note.id, "Updated content")

        assert updated is not None
        assert updated.content == "Updated content"

    async def test_delete_note(self, dbsession: AsyncSession):
        """Test deleting a note."""
        client = await self._create_client(dbsession)
        dao = NoteDAO(dbsession)

        note = await dao.create_note(client_id=client.id, content="To delete")
        fetched = await dao.get_by_id(note.id)
        assert fetched is not None

        await dao.delete_note(note.id)
        deleted = await dao.get_by_id(note.id)

        assert deleted is None
