from fastapi import APIRouter
from fao.src.core import settings

from .asti_expenditures import router as asti_expenditures
from .asti_researchers import router as asti_researchers

asti_api = APIRouter(
  prefix=f"/{settings.api_version_prefix}", 
  tags=["asti"],
)

asti_api.include_router(
  asti_expenditures, 
  prefix=f"/asti", 
  tags=["asti", "asti_expenditures"],
)
asti_api.include_router(
  asti_researchers, 
  prefix=f"/asti", 
  tags=["asti", "asti_researchers"],
)

asti_group_map = {
    "description": "asti",
    "routes": [
        {
            "name": "asti_expenditures",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/asti/asti_expenditures",
        },
        {
            "name": "asti_researchers",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/asti/asti_researchers",
        },
    ],
}

# Export the sub-API
__all__ = ["asti_api", "asti_group_map"]