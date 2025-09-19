import random
import string
import uuid
from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.models.agent import Agent
from abdullateef_api.db.models.booking import Booking
from abdullateef_api.db.models.client import Client
from abdullateef_api.db.models.commission import Commission


class AgentDAO:
    """Data Access Object for the Agent model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------
    # Internal Helpers
    # ------------------------------
    async def _generate_agent_code(self) -> str:
        """Generate a unique 5-character agent code with letters + digits."""
        while True:
            # ensure at least one letter and one digit
            letters = random.choices(string.ascii_uppercase, k=3)
            digits = random.choices(string.digits, k=2)
            code_list = letters + digits
            random.shuffle(code_list)
            code = "".join(code_list)

            # check uniqueness
            existing = await self.get_by_code(code)
            if not existing:
                return code

    # ------------------------------
    # Create
    # ------------------------------
    async def create_agent(
        self,
        first_name: str,
        last_name: str,
        agent_code: Optional[str] = None,
        other_name: Optional[str] = None,
        sex: Optional[str] = None,
        phone_number: Optional[str] = None,
        bank_name: Optional[str] = None,
        account_number: Optional[str] = None,
    ) -> Agent:
        """Create a new Agent."""
        if not agent_code:
            agent_code = await self._generate_agent_code()

        agent = Agent(
            first_name=first_name,
            last_name=last_name,
            other_name=other_name,
            sex=sex,
            phone_number=phone_number,
            bank_name=bank_name,
            account_number=account_number,
            agent_code=agent_code,
        )
        self.session.add(agent)
        await self.session.flush()
        return agent

    # ------------------------------
    # Get
    # ------------------------------
    async def get_by_id(self, agent_id: uuid.UUID) -> Optional[Agent]:
        result = await self.session.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, agent_code: str) -> Optional[Agent]:
        result = await self.session.execute(
            select(Agent).where(Agent.agent_code == agent_code),
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone_number: str) -> Optional[Agent]:
        result = await self.session.execute(
            select(Agent).where(Agent.phone_number == phone_number),
        )
        return result.scalar_one_or_none()

    async def filter_by_name(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> List[Agent]:
        stmt = select(Agent)
        if first_name:
            stmt = stmt.where(Agent.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.where(Agent.last_name.ilike(f"%{last_name}%"))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_agents(self, limit: int = 50, offset: int = 0) -> List[Agent]:
        result = await self.session.execute(select(Agent).limit(limit).offset(offset))
        return list(result.scalars().all())

    # ------------------------------
    # Update
    # ------------------------------
    async def update_agent(
        self,
        agent_id: uuid.UUID,
        **kwargs,
    ) -> Optional[Agent]:
        await self.session.execute(
            update(Agent).where(Agent.id == agent_id).values(**kwargs),
        )
        await self.session.flush()
        return await self.get_by_id(agent_id)

    async def regenerate_agent_code(self, agent_id: uuid.UUID) -> Optional[Agent]:
        """Generate and assign a new unique agent code to an existing agent."""
        new_code = await self._generate_agent_code()
        return await self.update_agent(agent_id, agent_code=new_code)

    # ------------------------------
    # Delete
    # ------------------------------
    async def delete_agent(self, agent_id: uuid.UUID) -> None:
        await self.session.execute(delete(Agent).where(Agent.id == agent_id))
        await self.session.flush()

    # ------------------------------
    # Relationship helpers
    # ------------------------------
    async def get_bookings(self, agent_id: uuid.UUID) -> List[Booking]:
        result = await self.session.execute(
            select(Booking).where(Booking.agent_id == agent_id),
        )
        return list(result.scalars().all())

    async def get_commissions(self, agent_id: uuid.UUID) -> List[Commission]:
        result = await self.session.execute(
            select(Commission).where(Commission.agent_id == agent_id),
        )
        return list(result.scalars().all())

    async def get_referred_clients(self, agent_id: uuid.UUID) -> List[Client]:
        result = await self.session.execute(
            select(Client).where(Client.referee_id == agent_id),
        )
        return list(result.scalars().all())
