import uuid
from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.models.note import Note


class NoteDAO:
    """Data Access Object for Note model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_note(
        self,
        client_id: uuid.UUID,
        content: str,
        created_by: Optional[uuid.UUID] = None,
    ) -> Note:
        """Create a new note."""
        note = Note(client_id=client_id, content=content, created_by=created_by)
        self.session.add(note)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def get_by_id(self, note_id: uuid.UUID) -> Optional[Note]:
        """Get a note by ID."""
        result = await self.session.execute(select(Note).where(Note.id == note_id))
        return result.scalar_one_or_none()

    async def get_by_client_id(self, client_id: uuid.UUID) -> List[Note]:
        """Get all notes for a given client."""
        result = await self.session.execute(
            select(Note).where(Note.client_id == client_id),
        )
        return result.scalars().all()

    async def get_by_created_by(self, created_by: uuid.UUID) -> List[Note]:
        """Get all notes created by a specific user."""
        result = await self.session.execute(
            select(Note).where(Note.created_by == created_by),
        )
        return result.scalars().all()

    async def list_all(self) -> List[Note]:
        """List all notes."""
        result = await self.session.execute(select(Note))
        return result.scalars().all()

    async def update_content(
        self, note_id: uuid.UUID, new_content: str,
    ) -> Optional[Note]:
        """Update the content of a note."""
        await self.session.execute(
            update(Note).where(Note.id == note_id).values(content=new_content),
        )
        await self.session.commit()
        return await self.get_by_id(note_id)

    async def delete_note(self, note_id: uuid.UUID) -> None:
        """Delete a note."""
        await self.session.execute(delete(Note).where(Note.id == note_id))
        await self.session.commit()
