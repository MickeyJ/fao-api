from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func

# Correct imports for FAO API project
from fao.src.db.database import get_db
from fao.src.core import settings
from fao.src.db.pipelines.prices.prices_model import Prices
from fao.src.db.pipelines.item_codes.item_codes_model import ItemCodes
from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

router = APIRouter(
    prefix=f"/{settings.api_version_prefix}/prices/multi-line",
    tags=["prices", "analytics", "visualizations", "multi-line"],
)

# Placeholder for the specific element code you'll determine
PRICE_ELEMENT_CODE = "5532"  # TODO: Replace with actual element code (e.g., Producer Price)

# {
#   "dataset": "prices",
#   "total_records": 1261761,
#   "flag_distribution": [
#     {
#       "flag": "A",
#       "description": "Official figure",
#       "record_count": 837045,
#       "percentage": 66.34
#     },
#     {
#       "flag": "I",
#       "description": "Imputed value",
#       "record_count": 420067,
#       "percentage": 33.29
#     },
#     {
#       "flag": "X",
#       "description": "Figure from international organizations",
#       "record_count": 4649,
#       "percentage": 0.37
#     }
#   ]
# }

# {
#   "dataset": "prices",
#   "total_elements": 4,
#   "elements": [
#     {
#       "element_code": "5530",
#       "element": "Producer Price (LCU/tonne)",
#       "record_count": 512874
#     },
#     {
#       "element_code": "5539",
#       "element": "Producer Price Index (2014-2016 = 100)",
#       "record_count": 419911
#     },
#     {
#       "element_code": "5531",
#       "element": "Producer Price (SLC/tonne)",
#       "record_count": 166274
#     },
#     {
#       "element_code": "5532",
#       "element": "Producer Price (USD/tonne)",
#       "record_count": 162702
#     }
#   ]
# }


@router.get("/price-data")
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
        raise HTTPException(
            status_code=422,
            detail={
                "errcode": 422,
                "message": "Missing item_code query parameter",
            },
        )

    if not (10 <= item_code <= 9999):
        raise HTTPException(
            status_code=422,
            detail={
                "errcode": 422,
                "message": "item_code must be between 10 and 9999",
            },
        )

    if not area_codes:
        raise HTTPException(
            status_code=422,
            detail={
                "errcode": 422,
                "message": "Missing area_codes query parameter",
            },
        )

    # Validate inputs
    if len(area_codes) > 5:
        raise HTTPException(
            status_code=422,
            detail={
                "errcode": 422,
                "message": "Maximum 5 area_codes allowed",
            },
        )

    results = get_multi_line_price_data(
        item_code,
        area_codes,
        year_start,
        year_end,
        db,
    )

    if not results:
        print(f"No data found for item {item_code} in areas {area_codes} from {year_start} to {year_end}")
        raise HTTPException(
            status_code=404,
            detail={
                "errcode": 404,
                "message": f"No data found for item {item_code} in areas {area_codes} from {year_start} to {year_end}",
            },
        )

    # Group data by area for D3.js consumption
    data_by_area = {}
    item_info = None
    units = set()

    for row in results:
        area_name = row["area_name"]

        # Store item info (should be same for all rows)
        if item_info is None:
            item_info = {"name": row["item_name"], "code": item_code}

        # Track units (instead of currencies for now)
        units.add(row["unit"])

        # Group by area
        if area_name not in data_by_area:
            data_by_area[area_name] = {
                "area_name": area_name,
                "area_code": row["area_code"],
                "currency": row["unit"],  # Using unit for now, will map to currency later
                "data_points": [],
            }

        data_by_area[area_name]["data_points"].append(
            {
                "year": row["year"],
                "price_per_t": row["price"],
                "price_per_kg": round(row["price"] / 1000, 4) if row["price"] else None,
                "price_per_lb": round(row["price"] / 2204.6, 4) if row["price"] else None,
            }
        )

    # Convert to list format that D3 likes
    lines_data = list(data_by_area.values())

    # Calculate some summary stats for the frontend
    all_prices = [
        point["price_per_t"] for area_data in lines_data for point in area_data["data_points"] if point["price_per_t"]
    ]
    all_years = [point["year"] for area_data in lines_data for point in area_data["data_points"]]

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
        "currencies": list(units),  # Will be units for now
        "quantities": "Prices are likely in USD per metric ton",
        "note": "Prices may show currency transitions/redenominations. Use caution when comparing across years.",
    }


@router.get("/items")
def get_all_items(db: Session = Depends(get_db)):
    """Get all food items with price data"""
    query = (
        select(
            ItemCodes.id,
            ItemCodes.item.label("name"),
            ItemCodes.item_code.label("item_code"),
            ItemCodes.item_code_cpc.label("cpc_code"),
            func.count(Prices.id).label("price_points"),
        )
        .join(Prices, ItemCodes.id == Prices.item_code_id)
        .join(Elements, Elements.id == Prices.element_code_id)
        .join(Flags, Flags.id == Prices.flag_id)
        .where(
            and_(Elements.element_code == PRICE_ELEMENT_CODE, ItemCodes.source_dataset == "prices", Flags.flag == "A")
        )
        .group_by(ItemCodes.id, ItemCodes.item, ItemCodes.item_code, ItemCodes.item_code_cpc)
        .order_by(func.count(Prices.id).desc(), ItemCodes.item)
    )

    results = db.execute(query).mappings().all()

    return {"items": [dict(item) for item in results]}


@router.get("/available-areas")
def get_available_data_for_item(
    item_code: int = Query(..., description="Item FAO code"),
    db: Session = Depends(get_db),
):
    """
    Get what countries and years have data for this item
    Useful for frontend to show available options
    """
    query = (
        select(
            AreaCodes.area.label("name"),
            AreaCodes.area_code.label("area_code"),
            func.min(Prices.year).label("earliest_year"),
            func.max(Prices.year).label("latest_year"),
            func.count(Prices.year).label("data_points"),
            Prices.unit,  # Using unit instead of currency for now
        )
        .join(ItemCodes, ItemCodes.id == Prices.item_code_id)
        .join(AreaCodes, AreaCodes.id == Prices.area_code_id)
        .join(Elements, Elements.id == Prices.element_code_id)
        .join(Flags, Flags.id == Prices.flag_id)
        .where(
            and_(ItemCodes.item_code == str(item_code), Elements.element_code == PRICE_ELEMENT_CODE, Flags.flag == "A")
        )
        .group_by(AreaCodes.area, AreaCodes.area_code, Prices.unit)
        .order_by(func.count(Prices.year).desc())
    )

    results = db.execute(query).mappings().all()

    return {
        "item_code": item_code,
        "available_areas": [dict(row) for row in results],
        "total_areas": len(results),
    }


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
            AreaCodes.area.label("area_name"),
            AreaCodes.area_code.label("area_code"),
            Prices.year,
            Prices.value.label("price"),
            Prices.unit,  # Using unit instead of currency
            ItemCodes.item.label("item_name"),
        )
        .join(ItemCodes, ItemCodes.id == Prices.item_code_id)
        .join(AreaCodes, AreaCodes.id == Prices.area_code_id)
        .join(Elements, Elements.id == Prices.element_code_id)
        .join(Flags, Flags.id == Prices.flag_id)
        .where(
            and_(
                Prices.year >= year_start,
                Prices.year <= year_end,
                ItemCodes.item_code == str(item_code),
                Elements.element_code == PRICE_ELEMENT_CODE,
                Flags.flag == "A",
            )
        )
    )

    # Filter by area_codes (FAO codes)
    area_conditions = []
    for area_code in area_codes:
        area_conditions.append(AreaCodes.area_code == str(area_code))

    query = query.where(or_(*area_conditions))

    # Order by area and year for clean data structure
    query = query.order_by(AreaCodes.area, Prices.year)

    # Execute query
    results = db.execute(query).mappings().all()

    return results
