from fastapi import APIRouter
from fao.src.core import settings

from .value_of_production import router as value_of_production
from .value_shares_industry_primary_factors import router as value_shares_industry_primary_factors

value_api = APIRouter(
  prefix=f"/{settings.api_version_prefix}", 
  # tags=["value"],
)

value_api.include_router(
  value_of_production, 
  prefix=f"/value", 
  tags=["value_of_production"],
)
value_api.include_router(
  value_shares_industry_primary_factors, 
  prefix=f"/value", 
  tags=["value_shares_industry_primary_factors"],
)

value_group_map = {
    "description": "value",
    "routes": [
        {
            "name": "value_of_production",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/value/value_of_production",
        },
        {
            "name": "value_shares_industry_primary_factors",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/value/value_shares_industry_primary_factors",
        },
    ],
}

# Export the sub-API
__all__ = ["value_api", "value_group_map"]