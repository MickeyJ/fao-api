from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, text
from typing import Optional
from db.database import get_db
from db.models import Item, Area, ItemPrice
from .. import current_version_prefix

router = APIRouter(
    prefix="/data",
    tags=["data"],
    responses={404: {"description": "Not found"}},
)

router_map = {
    f"{current_version_prefix}": {
        "items": f"/{current_version_prefix}/data/items",
        "areas": f"/{current_version_prefix}/data/items",
        "overview": f"/{current_version_prefix}/data/overview",
        "available-data-for-item": f"/{current_version_prefix}/data/available-data-for-item",
    }
}


@router.get("/items")
def get_all_items(db: Session = Depends(get_db)):
    """Get all 250 food items"""
    query = (
        select(
            Item.id,
            Item.name,
            Item.fao_code.label("item_code"),
            Item.cpc_code,
            func.count(ItemPrice.id).label("price_points"),
        )
        .join(ItemPrice, Item.id == ItemPrice.item_id)
        .group_by(Item.id, Item.name, Item.fao_code, Item.cpc_code)
        .order_by(
            func.count(ItemPrice.id).desc(), Item.name
        )  # Most price points first, then by name
    )

    results = db.execute(query).mappings().all()

    return {"items": [dict(item) for item in results]}


@router.get("/areas")
def get_all_areas(db: Session = Depends(get_db)):
    """Get all countries/areas"""
    query = select(Area.id, Area.name, Area.fao_code, Area.m49_code).order_by(Area.name)

    results = db.execute(query).mappings().all()

    return {"areas": [dict(area) for area in results]}


@router.get("/overview")
def get_data_overview(db: Session = Depends(get_db)):
    """Get high-level overview of available data"""
    # ... your implementation


# Helper endpoint to get available data for the item
@router.get("/available-data-for-item")
def get_available_data_for_item(
    item_code: int = Query(..., description="Item name or FAO code"),
    db: Session = Depends(get_db),
):
    """
    Get what countries and years have data for this item
    Useful for frontend to show available options
    """

    if not item_code:
        raise HTTPException(
            status_code=400,
            detail="Item code is required. Provide FAO code.",
        )

    query = (
        select(
            Area.name.label("name"),
            Area.fao_code.label("area_code"),
            func.min(ItemPrice.year).label("earliest_year"),
            func.max(ItemPrice.year).label("latest_year"),
            func.count(ItemPrice.year).label("data_points"),
            ItemPrice.currency,
        )
        .join(Item, Item.id == ItemPrice.item_id)
        .join(Area, Area.id == ItemPrice.area_id)
    )

    query = query.where(Item.fao_code == int(item_code))

    query = query.group_by(Area.name, Area.fao_code, ItemPrice.currency).order_by(
        func.count(ItemPrice.year).desc()
    )  # Most data first

    results = db.execute(query).mappings().all()

    return {
        "item_code": item_code,
        "available_areas": list(results),
        "total_areas": len(results),
    }
