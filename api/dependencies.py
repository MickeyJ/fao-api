from typing import List
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Item, Area, ItemPrice
from fastapi import Depends, HTTPException


def get_current_user():
    """Example shared dependency"""
    pass


def validate_year_range(year_start: int, year_end: int):
    """Shared validation function"""
    if year_start > year_end:
        raise HTTPException(400, "Start year must be before end year")
    return year_start, year_end


def get_multi_line_price_data(
    item_code: int,
    area_codes: List[int],
    year_start: int,
    year_end: int,
    db: Session,
):
    """
    Get price trend data for multi-line chart visualization
    Returns data optimized for D3.js multi-line charts
    """

    validate_year_range(year_start, year_end)

    # Build the query
    query = (
        select(
            Area.name.label("area_name"),
            Area.fao_code.label("area_code"),
            ItemPrice.year,
            ItemPrice.value.label("price"),
            ItemPrice.currency,
            Item.name.label("item_name"),
        )
        .join(Item, Item.id == ItemPrice.item_id)
        .join(Area, Area.id == ItemPrice.area_id)
        .where(
            and_(
                ItemPrice.year >= year_start,
                ItemPrice.year <= year_end,
                Item.fao_code == item_code,
            )
        )
    )

    # Filter by area_codes (FAO codes)
    area_conditions = []
    for area_code in area_codes:
        area_conditions.append(Area.fao_code == int(area_code))

    query = query.where(or_(*area_conditions))

    # Order by area and year for clean data structure
    query = query.order_by(Area.name, ItemPrice.year)

    # Execute query
    results = db.execute(query).mappings().all()

    return results
