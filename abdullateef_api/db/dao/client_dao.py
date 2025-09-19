import uuid
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.enums import CountryEnum, GenderEnum
from abdullateef_api.db.models.agent import Agent
from abdullateef_api.db.models.client import Client


class ClientDAO:
    """Data Access Object for Client model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_client(
        self,
        first_name: str,
        last_name: str,
        sex: GenderEnum,
        phone_number: str,
        passport_number: str,
        location: CountryEnum,
        other_name: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        referee_id: Optional[uuid.UUID] = None,
    ) -> Client:
        """Create and persist a new client."""
        client = Client(
            first_name=first_name,
            last_name=last_name,
            other_name=other_name,
            sex=sex,
            phone_number=phone_number,
            passport_number=passport_number,
            date_of_birth=date_of_birth,
            location=location,
            referee_id=referee_id,
        )
        self.session.add(client)
        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def get_by_id(self, client_id: uuid.UUID) -> Optional[Client]:
        """Fetch a client by ID."""
        result = await self.session.execute(
            select(Client).where(Client.id == client_id),
        )
        return result.scalars().first()

    async def get_all(self) -> List[Client]:
        """Fetch all clients."""
        result = await self.session.execute(select(Client))
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> List[Client]:
        """Fetch clients by first, last, or other name (case-insensitive)."""
        result = await self.session.execute(
            select(Client).where(
                or_(
                    Client.first_name.ilike(f"%{name}%"),
                    Client.last_name.ilike(f"%{name}%"),
                    Client.other_name.ilike(f"%{name}%"),
                ),
            ),
        )
        return list(result.scalars().all())

    async def update_client(
        self,
        client_id: uuid.UUID,
        **kwargs,
    ) -> Optional[Client]:
        """Update fields of a client and return the updated instance."""
        client = await self.get_by_id(client_id)
        if not client:
            return None

        for key, value in kwargs.items():
            if hasattr(client, key) and value is not None:
                setattr(client, key, value)

        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def delete_client(self, client_id: uuid.UUID) -> bool:
        """Delete a client by ID."""
        client = await self.get_by_id(client_id)
        if not client:
            return False

        await self.session.delete(client)
        await self.session.commit()
        return True

    async def get_by_passport(self, passport_number: str) -> Optional[Client]:
        """Fetch a client by passport number."""
        result = await self.session.execute(
            select(Client).where(Client.passport_number == passport_number),
        )
        return result.scalars().first()

    async def get_by_phone(self, phone_number: str) -> Optional[Client]:
        """Fetch a client by phone number."""
        result = await self.session.execute(
            select(Client).where(Client.phone_number == phone_number),
        )
        return result.scalars().first()

    async def get_by_referee(self, referee: uuid.UUID | str) -> List[Client]:
        """
        Fetch clients referred by a specific agent.
        Accepts either referee_id (UUID) or referee_code (string).
        """
        if isinstance(referee, uuid.UUID):
            # Search by referee_id
            result = await self.session.execute(
                select(Client).where(Client.referee_id == referee),
            )
        else:
            # Search by referee_code via join with Agent
            result = await self.session.execute(
                select(Client).join(Client.referee).where(Agent.agent_code == referee),
            )

        return list(result.scalars().all())

    async def get_by_location(self, location: CountryEnum) -> List[Client]:
        """Fetch clients by current location."""
        result = await self.session.execute(
            select(Client).where(Client.location == location),
        )
        return list(result.scalars().all())
