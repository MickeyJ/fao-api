from fastapi import APIRouter
from fao.src.core import settings

from .trade_crops_livestock_indicators import router as trade_crops_livestock_indicators
from .trade_crops_livestock import router as trade_crops_livestock
from .trade_detailed_trade_matrix import router as trade_detailed_trade_matrix
from .trade_indices import router as trade_indices

trade_api = APIRouter(
  prefix=f"/{settings.api_version_prefix}", 
  # tags=["trade"],
)

trade_api.include_router(
  trade_crops_livestock_indicators, 
  prefix=f"/trade", 
  tags=["trade_crops_livestock_indicators"],
)
trade_api.include_router(
  trade_crops_livestock, 
  prefix=f"/trade", 
  tags=["trade_crops_livestock"],
)
trade_api.include_router(
  trade_detailed_trade_matrix, 
  prefix=f"/trade", 
  tags=["trade_detailed_trade_matrix"],
)
trade_api.include_router(
  trade_indices, 
  prefix=f"/trade", 
  tags=["trade_indices"],
)

trade_group_map = {
    "description": "trade",
    "routes": [
        {
            "name": "trade_crops_livestock_indicators",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/trade/trade_crops_livestock_indicators",
        },
        {
            "name": "trade_crops_livestock",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/trade/trade_crops_livestock",
        },
        {
            "name": "trade_detailed_trade_matrix",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/trade/trade_detailed_trade_matrix",
        },
        {
            "name": "trade_indices",
            "description": "",
            "path": f"/{ settings.api_version_prefix }/trade/trade_indices",
        },
    ],
}

# Export the sub-API
__all__ = ["trade_api", "trade_group_map"]