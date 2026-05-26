from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    RETAIL = "Retail"
    OFFICE = "Office"
    HOTEL = "Hotel"
    LOGISTICS = "Logistics"
    RESIDENTIAL = "Residential"
    MIXED = "Mixed"
    DENKMAL = "Denkmal"


class ConversionPotential(str, Enum):
    MICRO_APARTMENTS = "Micro-Apartments"
    BOUTIQUE_HOTEL = "Boutique Hotel"
    ASSISTED_LIVING = "Assisted Living"
    LOGISTICS = "Logistics"
    SERVICED_APARTMENTS = "Serviced Apartments"


class AssetProfile(BaseModel):
    # --- Traceability ---
    source_file: str = Field(..., description="Filename for data traceability")
    extracted_at: datetime = Field(default_factory=datetime.utcnow)

    # --- Location ---
    location_city: str = Field(..., description="City where the asset is located, e.g. Tübingen")
    location_address: Optional[str] = Field(default=None, description="Street-level address if extractable")

    # --- Asset classification ---
    asset_class: AssetClass = Field(..., description="Primary classification of the asset")
    conversion_potential: list[ConversionPotential] = Field(
        default_factory=list,
        description="Possible use cases after redevelopment"
    )

    # --- Size & value ---
    plot_size_sqm: Optional[float] = Field(default=None, description="Plot size in square meters")