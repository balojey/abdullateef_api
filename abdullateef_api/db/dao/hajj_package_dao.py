from typing import List, Optional

from fastapi import Depends
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.dependencies import get_db_session
from abdullateef_api.db.models.hajj_package import HajjPackage


class HajjPackageDAO:
    """Class for accessing hajj_packages table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    # -------------------------------
    # CREATE
    # -------------------------------
    async def create_hajj_package(
        self,
        year: int,
        local_price: int,
        diaspora_price: int,
        registration_fee: int,
        commission_amount: int,
        description: Optional[str] = None,
    ) -> HajjPackage:
        """
        Create a new Hajj Package.

        :return: created HajjPackage instance.
        """
        package = HajjPackage(
            year=year,
            local_price=local_price,
            diaspora_price=diaspora_price,
            registration_fee=registration_fee,
            commission_amount=commission_amount,
            description=description,
        )
        self.session.add(package)
        await self.session.flush()  # ensures ID is generated
        return package

    # -------------------------------
    # READ
    # -------------------------------
    async def get_all_packages(
        self, limit: int = 100, offset: int = 0,
    ) -> List[HajjPackage]:
        """
        Get all Hajj Packages with pagination.
        """
        result = await self.session.execute(
            select(HajjPackage).limit(limit).offset(offset),
        )
        return list(result.scalars().fetchall())

    async def get_package_by_id(self, package_id: str) -> Optional[HajjPackage]:
        """
        Get a specific Hajj Package by ID.
        """
        result = await self.session.execute(
            select(HajjPackage).where(HajjPackage.id == package_id),
        )
        return result.scalar_one_or_none()

    async def get_package_by_year(self, year: int) -> Optional[HajjPackage]:
        """
        Get the package for a specific year.
        """
        result = await self.session.execute(
            select(HajjPackage).where(HajjPackage.year == year),
        )
        return result.scalar_one_or_none()

    # -------------------------------
    # UPDATE
    # -------------------------------
    async def update_package(
        self,
        package_id: str,
        **kwargs,
    ) -> Optional[HajjPackage]:
        """
        Update fields of a Hajj Package.

        Example:
            await dao.update_package(package_id, local_price=5000, description="Updated")
        """
        await self.session.execute(
            update(HajjPackage)
            .where(HajjPackage.id == package_id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch"),
        )
        result = await self.session.execute(
            select(HajjPackage).where(HajjPackage.id == package_id),
        )
        return result.scalar_one_or_none()

    # -------------------------------
    # DELETE
    # -------------------------------
    async def delete_package(self, package_id: str) -> None:
        """
        Delete a Hajj Package by ID.
        """
        result = await self.session.execute(
            delete(HajjPackage).where(HajjPackage.id == package_id),
        )
        await self.session.commit()
        return result.rowcount > 0
