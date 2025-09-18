import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from abdullateef_api.db.dao.hajj_package_dao import HajjPackageDAO


@pytest.mark.anyio
async def test_create_and_get_package(dbsession: AsyncSession) -> None:
    """Test creation and retrieval of a Hajj Package."""
    dao = HajjPackageDAO(dbsession)

    package = await dao.create_hajj_package(
        year=2025,
        local_price=1000000,
        diaspora_price=1500000,
        registration_fee=500000,
        commission_amount=100000,
        description="Test package",
    )

    # Flush but don't commit yet
    await dbsession.flush()

    # Fetch by ID
    fetched = await dao.get_package_by_id(str(package.id))
    assert fetched is not None
    assert fetched.year == 2025
    assert fetched.local_price == 1000000
    assert fetched.diaspora_price == 1500000
    assert fetched.registration_fee == 500000
    assert fetched.commission_amount == 100000
    assert fetched.description == "Test package"

    # Fetch by year
    same_year = await dao.get_package_by_year(2025)
    assert same_year is not None
    assert same_year.id == package.id


@pytest.mark.anyio
async def test_get_all_packages(dbsession: AsyncSession) -> None:
    """Test listing multiple Hajj Packages."""
    dao = HajjPackageDAO(dbsession)

    # Create 3 packages
    for y in [2023, 2024, 2025]:
        await dao.create_hajj_package(
            year=y,
            local_price=1000 * y,
            diaspora_price=2000 * y,
            registration_fee=500,
            commission_amount=50,
            description=f"Package {y}",
        )
    await dbsession.flush()

    results = await dao.get_all_packages(limit=10, offset=0)
    years = [p.year for p in results]
    assert 2023 in years and 2024 in years and 2025 in years
    assert len(results) >= 3


@pytest.mark.anyio
async def test_update_package(dbsession: AsyncSession) -> None:
    """Test updating fields of a Hajj Package."""
    dao = HajjPackageDAO(dbsession)

    package = await dao.create_hajj_package(
        year=2026,
        local_price=5000,
        diaspora_price=7000,
        registration_fee=2000,
        commission_amount=100,
        description="Old desc",
    )
    await dbsession.flush()

    updated = await dao.update_package(
        str(package.id),
        local_price=9999,
        description="New description",
    )
    assert updated is not None
    assert updated.local_price == 9999
    assert updated.description == "New description"


@pytest.mark.anyio
async def test_delete_package(dbsession: AsyncSession) -> None:
    """Test deleting a Hajj Package."""
    dao = HajjPackageDAO(dbsession)

    package = await dao.create_hajj_package(
        year=2030,
        local_price=10000,
        diaspora_price=20000,
        registration_fee=3000,
        commission_amount=200,
    )
    await dbsession.flush()

    # Ensure it's there
    fetched = await dao.get_package_by_id(str(package.id))
    assert fetched is not None

    # Delete
    await dao.delete_package(str(package.id))
    await dbsession.flush()

    # Ensure it's gone
    deleted = await dao.get_package_by_id(str(package.id))
    assert deleted is None


@pytest.mark.anyio
async def test_nonexistent_package_queries(dbsession: AsyncSession) -> None:
    """Ensure querying non-existent package returns None."""
    dao = HajjPackageDAO(dbsession)

    fake_id = str(uuid.uuid4())
    by_id = await dao.get_package_by_id(fake_id)
    assert by_id is None

    by_year = await dao.get_package_by_year(2099)
    assert by_year is None
