from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from abdullateef_api.db.dao.hajj_package_dao import HajjPackageDAO
from abdullateef_api.web.api.hajj_package.schema import (
    HajjPackageDTO,
    HajjPackageInputDTO,
    HajjPackageUpdateDTO,
)

router = APIRouter()

# Create
@router.post("/", response_model=HajjPackageDTO)
async def create_hajj_package(
    payload: HajjPackageInputDTO,
    dao: HajjPackageDAO = Depends(),
):
    package = await dao.create_hajj_package(**payload.dict())
    return package

# Get all
@router.get("/", response_model=List[HajjPackageDTO])
async def list_hajj_package(
    dao: HajjPackageDAO = Depends(),
):
    return await dao.get_all_packages()

# Get by ID
@router.get("/{package_id}", response_model=HajjPackageDTO)
async def get_hajj_package(
    package_id: UUID,
    dao: HajjPackageDAO = Depends(),
):
    package = await dao.get_package_by_id(package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Hajj package not found")
    return package

# Update
@router.put("/{package_id}", response_model=HajjPackageDTO)
async def update_hajj_package(
    package_id: UUID,
    payload: HajjPackageUpdateDTO,
    dao: HajjPackageDAO = Depends(),
):
    package = await dao.update_package(package_id, **payload.dict(exclude_unset=True))
    if not package:
        raise HTTPException(status_code=404, detail="Hajj package not found")
    return package

# Delete
@router.delete("/{package_id}", status_code=204)
async def delete_hajj_package(
    package_id: UUID,
    dao: HajjPackageDAO = Depends(),
):
    success = await dao.delete_package(package_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hajj package not found")
