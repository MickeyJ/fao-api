from fastapi import APIRouter
from fao.src.core import settings

from .environment_bioenergy import router as environment_bioenergy
from .environment_cropland_nutrient_budget import router as environment_cropland_nutrient_budget
from .environment_emissions_intensities import router as environment_emissions_intensities
from .environment_land_cover import router as environment_land_cover
from .environment_livestock_manure import router as environment_livestock_manure
from .environment_livestock_patterns import router as environment_livestock_patterns
from .environment_temperature_change import router as environment_temperature_change

environment_api = APIRouter(
  prefix=f"/{settings.api_version_prefix}", 
  # tags=["environment"],
)

environment_api.include_router(
  environment_bioenergy, 
  prefix=f"/environment", 
  tags=["environment_bioenergy"],
)
environment_api.include_router(
  environment_cropland_nutrient_budget, 
  prefix=f"/environment", 
  tags=["environment_cropland_nutrient_budget"],
)
environment_api.include_router(
  environment_emissions_intensities, 
  prefix=f"/environment", 
  tags=["environment_emissions_intensities"],
)
environment_api.include_router(
  environment_land_cover, 
  prefix=f"/environment", 
  tags=["environment_land_cover"],
)
environment_api.include_router(
  environment_livestock_manure, 
  prefix=f"/environment", 
  tags=["environment_livestock_manure"],
)
environment_api.include_router(
  environment_livestock_patterns, 
  prefix=f"/environment", 
  tags=["environment_livestock_patterns"],
)
environment_api.include_router(
  environment_temperature_change, 
  prefix=f"/environment", 
  tags=["environment_temperature_change"],
)

environment_group_map = {
    "description": "environment",
    "routes": [
        {
            "name": "environment_bioenergy",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/environment/environment_bioenergy",
        },
        {
            "name": "environment_cropland_nutrient_budget",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/environment/environment_cropland_nutrient_budget",
        },
        {
            "name": "environment_emissions_intensities",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/environment/environment_emissions_intensities",
        },
        {
            "name": "environment_land_cover",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/environment/environment_land_cover",
        },
        {
            "name": "environment_livestock_manure",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/environment/environment_livestock_manure",
        },
        {
            "name": "environment_livestock_patterns",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/environment/environment_livestock_patterns",
        },
        {
            "name": "environment_temperature_change",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/environment/environment_temperature_change",
        },
    ],
}

# Export the sub-API
__all__ = ["environment_api", "environment_group_map"]