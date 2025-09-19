import uuid

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
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


@pytest.mark.anyio
@pytest.mark.parametrize(
    "year,local_price,diaspora_price,description",
    [
        (2025, 1000000, 1500000, "Premium Hajj package"),
        (2026, 2000000, 2500000, "Standard Hajj package"),
    ],
)
async def test_create_package_route(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    year: int,
    local_price: int,
    diaspora_price: int,
    description: str,
) -> None:
    """Test creating Hajj packages via API route (parameterized)."""
    url = fastapi_app.url_path_for("create_hajj_package")

    payload = {
        "year": year,
        "local_price": local_price,
        "diaspora_price": diaspora_price,
        "registration_fee": 500000,
        "commission_amount": 100000,
        "description": description,
    }

    response = await client.post(url, json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["year"] == year
    assert data["description"] == description

    # Confirm in DB
    dao = HajjPackageDAO(dbsession)
    package = await dao.get_package_by_id(data["id"])
    assert package is not None
    assert package.year == year


@pytest.mark.anyio
@pytest.mark.parametrize("years", [[2023, 2024], [2030, 2031, 2032]])
async def test_list_packages_route(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    years: list[int],
) -> None:
    """Test listing multiple Hajj packages via API route."""
    dao = HajjPackageDAO(dbsession)

    for y in years:
        await dao.create_hajj_package(
            year=y,
            local_price=1000 * y,
            diaspora_price=2000 * y,
            registration_fee=500,
            commission_amount=50,
            description=f"Package {y}",
        )
    await dbsession.flush()

    url = fastapi_app.url_path_for("list_hajj_package")
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    retrieved_years = [pkg["year"] for pkg in data]
    for y in years:
        assert y in retrieved_years


@pytest.mark.anyio
async def test_get_package_by_id_and_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test retrieving existing and non-existing Hajj package by ID via API route."""
    dao = HajjPackageDAO(dbsession)
    package = await dao.create_hajj_package(
        year=2030,
        local_price=5000,
        diaspora_price=7000,
        registration_fee=2000,
        commission_amount=100,
        description="Special package",
    )
    await dbsession.flush()

    # Existing
    url = fastapi_app.url_path_for("get_hajj_package", package_id=str(package.id))
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == "Special package"

    # Non-existing
    fake_id = str(uuid.uuid4())
    url = fastapi_app.url_path_for("get_hajj_package", package_id=fake_id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Hajj package not found"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "update_payload,expected_field,expected_value",
    [
        ({"description": "Updated package"}, "description", "Updated package"),
        ({"local_price": 7777}, "local_price", 7777),
    ],
)
async def test_update_package_route(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    update_payload: dict,
    expected_field: str,
    expected_value,
) -> None:
    """Test updating fields of a Hajj package via API route (parameterized)."""
    dao = HajjPackageDAO(dbsession)
    package = await dao.create_hajj_package(
        year=2040,
        local_price=10000,
        diaspora_price=20000,
        registration_fee=3000,
        commission_amount=200,
        description="Old description",
    )
    await dbsession.flush()

    url = fastapi_app.url_path_for("update_hajj_package", package_id=str(package.id))
    response = await client.put(url, json=update_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[expected_field] == expected_value

    # Non-existent update
    fake_id = str(uuid.uuid4())
    url = fastapi_app.url_path_for("update_hajj_package", package_id=fake_id)
    response = await client.put(url, json={"description": "Does not exist"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Hajj package not found"


@pytest.mark.anyio
async def test_delete_package_and_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test deleting an existing Hajj package and handling non-existent deletion."""
    dao = HajjPackageDAO(dbsession)
    package = await dao.create_hajj_package(
        year=2050,
        local_price=1111,
        diaspora_price=2222,
        registration_fee=333,
        commission_amount=44,
    )
    await dbsession.flush()

    # Delete existing
    url = fastapi_app.url_path_for("delete_hajj_package", package_id=str(package.id))
    response = await client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted = await dao.get_package_by_id(str(package.id))
    assert deleted is None

    # Delete non-existing
    fake_id = str(uuid.uuid4())
    url = fastapi_app.url_path_for("delete_hajj_package", package_id=fake_id)
    response = await client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Hajj package not found"


# ----------------------
# 🚨 Negative Validation Tests
# ----------------------


@pytest.mark.anyio
@pytest.mark.parametrize(
    "payload,expected_status",
    [
        # Missing required fields
        ({}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        # Negative price values
        (
            {
                "year": 2025,
                "local_price": -100,
                "diaspora_price": 200,
                "registration_fee": 50,
                "commission_amount": 10,
                "description": "Invalid package",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        # Wrong type for year (string instead of int)
        (
            {
                "year": "twenty-twenty-five",
                "local_price": 100,
                "diaspora_price": 200,
                "registration_fee": 50,
                "commission_amount": 10,
                "description": "Bad year type",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
    ],
)
async def test_invalid_package_payloads(
    fastapi_app: FastAPI,
    client: AsyncClient,
    payload: dict,
    expected_status: int,
) -> None:
    """Test invalid payloads are rejected by HajjPackage routes."""
    url = fastapi_app.url_path_for("create_hajj_package")
    response = await client.post(url, json=payload)
    assert response.status_code == expected_status
