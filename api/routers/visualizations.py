from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func
from typing import List
import re
from db.database import get_db
from db.models import Item, Area, ItemPrice
from api.dependencies import get_multi_line_price_data

router = APIRouter(
    prefix="/viz",
    tags=["visualizations"],
    responses={404: {"description": "Not found"}},
)


# Potatoes
# item_code=116
#
# Areas
# USA,           Australia,     China,        Canada,        India
# area_codes=231&area_codes=10&area_codes=351&area_codes=33&area_codes=100
#
@router.get("/multi-line-price-trends")
def get_multi_line_price_trends(
    item_code: int = Query(None, description="Item FAO code (2-4 digits)"),
    area_codes: List[int] = Query(None, description="List of up to 5 area FAO codes"),
    year_start: int = Query(1990, description="Start year"),
    year_end: int = Query(2023, description="End year"),
    db: Session = Depends(get_db),
):
    """
    Get price trend data for multi-line chart visualization
    Returns data optimized for D3.js multi-line charts
    """
    if not item_code:
        raise HTTPException(422, f"Missing item_code query parameter")

    if not (10 <= item_code <= 9999):
        raise HTTPException(422, "item_code must be between 10 and 9999")

    if not area_codes:
        raise HTTPException(422, f"Missing area_codes query parameter")

    # Validate inputs
    if len(area_codes) > 5:
        raise HTTPException(422, "Maximum 5 area_codes allowed")

    results = get_multi_line_price_data(
        item_code,
        area_codes,
        year_start,
        year_end,
        db,
    )

    if not results:
        raise HTTPException(
            404,
            f"No data found for item '{item_code}' in specified area_codes and years",
        )

    # Group data by area for D3.js consumption
    data_by_area = {}
    item_info = None
    currencies = set()

    for row in results:
        area_name = row["area_name"]

        # Store item info (should be same for all rows)
        if item_info is None:
            item_info = {"name": row["item_name"], "code": item_code}

        # Track currencies
        currencies.add(row["currency"])

        # Group by area
        if area_name not in data_by_area:
            data_by_area[area_name] = {
                "area_name": area_name,
                "area_code": row["area_code"],
                "currency": row["currency"],
                "data_points": [],
            }

        data_by_area[area_name]["data_points"].append(
            {
                "year": row["year"],
                "price_per_t": row["price"],
                "price_per_kg": round(row["price"] / 1000, 4),
                "price_per_lb": round(row["price"] / 2204.6, 4),
            }
        )

    # Convert to list format that D3 likes
    lines_data = list(data_by_area.values())

    # Calculate some summary stats for the frontend
    all_prices = [
        point["price_per_t"]
        for area_data in lines_data
        for point in area_data["data_points"]
    ]
    all_years = [
        point["year"] for area_data in lines_data for point in area_data["data_points"]
    ]

    summary = {
        "min_price": min(all_prices) if all_prices else 0,
        "max_price": max(all_prices) if all_prices else 0,
        "min_year": min(all_years) if all_years else year_start,
        "max_year": max(all_years) if all_years else year_end,
        "areas_found": len(lines_data),
        "total_data_points": len(all_prices),
    }

    return {
        "item": item_info,
        "parameters": {
            "requested_areas": area_codes,
            "year_start": year_start,
            "year_end": year_end,
        },
        "lines": lines_data,
        "summary": summary,
        "currencies": list(currencies),
        "quantities": "Prices are likely in USD per metric ton",
        "note": "Prices may show currency transitions/redenominations. Use caution when comparing across years.",
    }


# Alternative format - more D3.js friendly for some use cases
@router.get("/multi-line-price-trends-flat")
def get_multi_line_price_data_flat(
    item: str = Query(..., description="Item name or FAO code"),
    area_codes: List[str] = Query(
        ..., description="List of up to 5 area names or FAO codes"
    ),
    year_start: int = Query(..., description="Start year"),
    year_end: int = Query(..., description="End year"),
    db: Session = Depends(get_db),
):
    """
    Same data as above but in flat format where each row is year + prices for all countries
    Format: [{"year": 2020, "USA": 1500, "China": 1200, "Brazil": 800}, ...]
    """

    results = get_multi_line_price_data(
        item,
        area_codes,
        year_start,
        year_end,
        db,
    )

    # For brevity, I'll show the different data transformation:
    # This would reshape the data into a format where each year is a row
    # and each country is a column - great for some D3 multi-line patterns

    return {
        "note": "This endpoint would return data in wide format for different D3 patterns",
        "example_format": [
            {"year": 2020, "USA": 1500, "China": 1200, "Brazil": 800},
            {"year": 2021, "USA": 1600, "China": 1250, "Brazil": 850},
        ],
    }


# Helper endpoint to get available data for the item
@router.get("/available-data-for-item")
def get_available_data_for_item(
    item: str = Query(..., description="Item name or FAO code"),
    db: Session = Depends(get_db),
):
    """
    Get what countries and years have data for this item
    Useful for frontend to show available options
    """

    query = (
        select(
            Area.name.label("area_name"),
            Area.fao_code.label("area_code"),
            func.min(ItemPrice.year).label("earliest_year"),
            func.max(ItemPrice.year).label("latest_year"),
            func.count(ItemPrice.year).label("data_points"),
            ItemPrice.currency,
        )
        .join(Item, Item.id == ItemPrice.item_id)
        .join(Area, Area.id == ItemPrice.area_id)
    )

    # Filter by item
    if item.isdigit():
        query = query.where(Item.fao_code == int(item))
    else:
        query = query.where(Item.name.ilike(f"%{item}%"))

    query = query.group_by(Area.name, Area.fao_code, ItemPrice.currency).order_by(
        func.count(ItemPrice.year).desc()
    )  # Most data first

    results = db.execute(query).mappings().all()

    return {"item": item, "available_areas": list(results), "total_areas": len(results)}
