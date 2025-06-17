from fastapi import APIRouter
from fao.src.core import settings

from .commodity_balances_non_food_2013_old_methodology import router as commodity_balances_non_food_2013_old_methodology
from .commodity_balances_non_food_2010 import router as commodity_balances_non_food_2010

commodity_api = APIRouter(
  prefix=f"/{settings.api_version_prefix}", 
  # tags=["commodity"],
)

commodity_api.include_router(
  commodity_balances_non_food_2013_old_methodology, 
  prefix=f"/commodity", 
  tags=["commodity_balances_non_food_2013_old_methodology"],
)
commodity_api.include_router(
  commodity_balances_non_food_2010, 
  prefix=f"/commodity", 
  tags=["commodity_balances_non_food_2010"],
)

commodity_group_map = {
    "description": "commodity",
    "routes": [
        {
            "name": "commodity_balances_non_food_2013_old_methodology",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/commodity/commodity_balances_non_food_2013_old_methodology",
        },
        {
            "name": "commodity_balances_non_food_2010",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/commodity/commodity_balances_non_food_2010",
        },
    ],
}

# Export the sub-API
__all__ = ["commodity_api", "commodity_group_map"]