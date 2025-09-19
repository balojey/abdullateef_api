from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HajjPackageDTO(BaseModel):
    """
    DTO for returning Hajj Packages from the API.
    """

    id: UUID
    year: int
    local_price: float
    diaspora_price: float
    registration_fee: float
    commission_amount: float
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HajjPackageInputDTO(BaseModel):
    """
    DTO for creating a new Hajj Package.
    """

    year: int = Field(..., ge=2000, description="Package year must be >= 2000")
    local_price: float = Field(..., ge=0, description="Local price must be non-negative")
    diaspora_price: float = Field(..., ge=0, description="Diaspora price must be non-negative")
    registration_fee: float = Field(..., ge=0, description="Registration fee must be non-negative")
    commission_amount: float = Field(..., ge=0, description="Commission amount must be non-negative")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description of the package")


class HajjPackageUpdateDTO(BaseModel):
    """
    DTO for updating an existing Hajj Package (partial updates allowed).
    """

    year: Optional[int] = Field(None, ge=2000)
    local_price: Optional[float] = Field(None, ge=0)
    diaspora_price: Optional[float] = Field(None, ge=0)
    registration_fee: Optional[float] = Field(None, ge=0)
    commission_amount: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=1000)
