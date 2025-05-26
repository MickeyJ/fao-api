from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_, desc, asc
from typing import Optional, List
from db.database import get_db
from db.models import Item, Area, ItemPrice

app = FastAPI(title="Food Price Analysis API")


@app.get("/data/items")
def get_all_items(
    limit: Optional[int] = Query(None, description="Limit number of results"),
    db: Session = Depends(get_db),
):
    """Get all available food items/commodities"""
    query = (
        select(
            Item.fao_code,
            Item.name,
            Item.cpc_code,
            func.count(ItemPrice.id).label("price_records"),
            func.min(ItemPrice.year).label("earliest_year"),
            func.max(ItemPrice.year).label("latest_year"),
        )
        .outerjoin(ItemPrice, Item.id == ItemPrice.item_id)
        .group_by(Item.fao_code, Item.name, Item.cpc_code)
        .order_by(Item.name)
    )

    if limit:
        query = query.limit(limit)

    results = db.execute(query).mappings().all()
    return {"items": list(results), "total": len(results)}


@app.get("/data/areas")
def get_all_areas(
    limit: Optional[int] = Query(None, description="Limit number of results"),
    db: Session = Depends(get_db),
):
    """Get all available countries/areas"""
    query = (
        select(
            Area.fao_code,
            Area.name,
            Area.m49_code,
            func.count(ItemPrice.id).label("price_records"),
            func.min(ItemPrice.year).label("earliest_year"),
            func.max(ItemPrice.year).label("latest_year"),
        )
        .outerjoin(ItemPrice, Area.id == ItemPrice.area_id)
        .group_by(Area.fao_code, Area.name, Area.m49_code)
        .order_by(Area.name)
    )

    if limit:
        query = query.limit(limit)

    results = db.execute(query).mappings().all()
    return {"areas": list(results), "total": len(results)}


@app.get("/data/overview")
def get_data_overview(db: Session = Depends(get_db)):
    """Get high-level overview of available data"""
    item_count = db.execute(select(func.count(Item.id))).scalar()
    area_count = db.execute(select(func.count(Area.id))).scalar()
    price_record_count = db.execute(select(func.count(ItemPrice.id))).scalar()

    year_range = db.execute(
        select(func.min(ItemPrice.year), func.max(ItemPrice.year))
    ).first()

    return {
        "total_items": item_count,
        "total_areas": area_count,
        "total_price_records": price_record_count,
        "year_range": {"start": year_range[0], "end": year_range[1]},
    }


@app.get("/data/currencies")
def get_available_currencies(db: Session = Depends(get_db)):
    """Get all currencies present in the data"""
    results = (
        db.execute(
            select(ItemPrice.currency, func.count(ItemPrice.id).label("record_count"))
            .group_by(ItemPrice.currency)
            .order_by(ItemPrice.currency)
        )
        .mappings()
        .all()
    )

    return {"currencies": list(results)}


@app.get("/analysis/price-trends")
def get_price_trends(
    item: Optional[str] = Query(None, description="Item name or FAO code"),
    area: Optional[str] = Query(None, description="Area name or FAO code"),
    year_start: Optional[int] = Query(1993, description="Start year"),
    year_end: Optional[int] = Query(2024, description="End year"),
    db: Session = Depends(get_db),
):
    """Get price trends over time for specific items and areas"""
    query = (
        select(
            Item.name.label("item_name"),
            Area.name.label("area_name"),
            ItemPrice.year,
            ItemPrice.value.label("price"),
            ItemPrice.currency,
        )
        .join(Item, Item.id == ItemPrice.item_id)
        .join(Area, Area.id == ItemPrice.area_id)
        .where(and_(ItemPrice.year >= year_start, ItemPrice.year <= year_end))
    )

    # Add filters
    if item:
        if item.isdigit():
            query = query.where(Item.fao_code == int(item))
        else:
            query = query.where(Item.name.ilike(f"%{item}%"))

    if area:
        if area.isdigit():
            query = query.where(Area.fao_code == int(area))
        else:
            query = query.where(Area.name.ilike(f"%{area}%"))

    query = query.order_by(Item.name, Area.name, ItemPrice.year)
    results = db.execute(query).mappings().all()

    return {"trends": list(results)}


@app.get("/analysis/price-comparison")
def compare_prices_across_countries(
    item: str = Query(..., description="Item name or FAO code"),
    year: Optional[int] = Query(2022, description="Year to compare"),
    limit: int = Query(20, description="Number of countries to return"),
    sort_by: str = Query(
        "price_desc", description="Sort by: price_asc, price_desc, country_name"
    ),
    db: Session = Depends(get_db),
):
    """Compare prices of a commodity across different countries"""
    query = (
        select(
            Area.name.label("country"),
            Area.fao_code.label("area_code"),
            ItemPrice.value.label("price"),
            ItemPrice.currency,
            Item.name.label("item_name"),
        )
        .join(Item, Item.id == ItemPrice.item_id)
        .join(Area, Area.id == ItemPrice.area_id)
        .where(ItemPrice.year == year)
    )

    # Filter by item
    if item.isdigit():
        query = query.where(Item.fao_code == int(item))
    else:
        query = query.where(Item.name.ilike(f"%{item}%"))

    # Add sorting
    if sort_by == "price_asc":
        query = query.order_by(asc(ItemPrice.value))
    elif sort_by == "price_desc":
        query = query.order_by(desc(ItemPrice.value))
    else:
        query = query.order_by(Area.name)

    query = query.limit(limit)
    results = db.execute(query).mappings().all()

    if not results:
        raise HTTPException(404, f"No data found for item '{item}' in year {year}")

    return {"comparison": list(results), "year": year, "total_countries": len(results)}


@app.get("/analysis/price-rankings")
def get_price_rankings(
    year: Optional[int] = Query(2022, description="Year to analyze"),
    ranking_type: str = Query(
        "most_expensive", description="most_expensive, least_expensive, most_volatile"
    ),
    area: Optional[str] = Query(None, description="Filter by specific area"),
    limit: int = Query(10, description="Number of results"),
    db: Session = Depends(get_db),
):
    """Get rankings of most/least expensive commodities or most volatile prices"""

    # Validate ranking_type
    valid_types = ["most_expensive", "least_expensive", "most_volatile"]
    if ranking_type not in valid_types:
        raise HTTPException(400, f"Invalid ranking_type. Must be one of: {valid_types}")

    if ranking_type in ["most_expensive", "least_expensive"]:
        query = (
            select(
                Item.name.label("item_name"),
                Area.name.label("area_name"),
                ItemPrice.value.label("average_price"),
                ItemPrice.currency,
            )
            .join(Item, Item.id == ItemPrice.item_id)
            .join(Area, Area.id == ItemPrice.area_id)
            .where(ItemPrice.year == year)
        )

        if area:
            if area.isdigit():
                query = query.where(Area.fao_code == int(area))
            else:
                query = query.where(Area.name.ilike(f"%{area}%"))

        if ranking_type == "most_expensive":
            query = query.order_by(desc(ItemPrice.value))
        else:
            query = query.order_by(asc(ItemPrice.value))

        query = query.limit(limit)

    else:  # ranking_type == "most_volatile"
        # Calculate coefficient of variation (std dev / mean) as volatility measure
        start_year = (year or 2022) - 5  # Handle None case
        subquery = (
            select(
                ItemPrice.item_id,
                ItemPrice.area_id,
                func.stddev(ItemPrice.value).label("std_dev"),
                func.avg(ItemPrice.value).label("avg_price"),
                (func.stddev(ItemPrice.value) / func.avg(ItemPrice.value)).label(
                    "volatility"
                ),
            )
            .where(ItemPrice.year >= start_year)
            .group_by(ItemPrice.item_id, ItemPrice.area_id)
            .having(func.count(ItemPrice.value) >= 3)
            .subquery()
        )

        query = (
            select(
                Item.name.label("item_name"),
                Area.name.label("area_name"),
                subquery.c.avg_price,
                subquery.c.volatility,
            )
            .join(Item, Item.id == subquery.c.item_id)
            .join(Area, Area.id == subquery.c.area_id)
            .order_by(desc(subquery.c.volatility))
            .limit(limit)
        )

    results = db.execute(query).mappings().all()
    return {"rankings": list(results), "type": ranking_type, "year": year}


@app.get("/analysis/inflation-rates")
def calculate_inflation_rates(
    item: Optional[str] = Query(None, description="Item name or FAO code"),
    area: Optional[str] = Query(None, description="Area name or FAO code"),
    years_back: int = Query(
        5, description="Number of years to calculate inflation over"
    ),
    current_year: int = Query(2023, description="Current year for calculation"),
    db: Session = Depends(get_db),
):
    """Calculate price inflation rates for commodities"""
    base_year = current_year - years_back

    # Get prices for both years
    current_prices = (
        select(
            ItemPrice.item_id, ItemPrice.area_id, ItemPrice.value.label("current_price")
        )
        .where(ItemPrice.year == current_year)
        .subquery()
    )

    base_prices = (
        select(
            ItemPrice.item_id, ItemPrice.area_id, ItemPrice.value.label("base_price")
        )
        .where(ItemPrice.year == base_year)
        .subquery()
    )

    # Calculate inflation rate
    query = (
        select(
            Item.name.label("item_name"),
            Area.name.label("area_name"),
            base_prices.c.base_price,
            current_prices.c.current_price,
            (
                (current_prices.c.current_price - base_prices.c.base_price)
                / base_prices.c.base_price
                * 100
            ).label("inflation_rate"),
        )
        .join(current_prices, and_(Item.id == current_prices.c.item_id))
        .join(
            base_prices,
            and_(
                Item.id == base_prices.c.item_id,
                current_prices.c.area_id == base_prices.c.area_id,
            ),
        )
        .join(Area, Area.id == current_prices.c.area_id)
    )

    # Add filters
    if item:
        if item.isdigit():
            query = query.where(Item.fao_code == int(item))
        else:
            query = query.where(Item.name.ilike(f"%{item}%"))

    if area:
        if area.isdigit():
            query = query.where(Area.fao_code == int(area))
        else:
            query = query.where(Area.name.ilike(f"%{area}%"))

    query = query.order_by(
        desc(
            func.abs(
                (
                    (current_prices.c.current_price - base_prices.c.base_price)
                    / base_prices.c.base_price
                    * 100
                )
            )
        )
    )

    results = db.execute(query).mappings().all()
    return {
        "period": f"{base_year}-{current_year}",
        "years_analyzed": years_back,
        "inflation_data": list(results),
    }


@app.get("/analysis/summary-stats")
def get_summary_statistics(
    item: Optional[str] = Query(None, description="Item name or FAO code"),
    area: Optional[str] = Query(None, description="Area name or FAO code"),
    year_start: Optional[int] = Query(1993, description="Start year"),
    year_end: Optional[int] = Query(2024, description="End year"),
    db: Session = Depends(get_db),
):
    """Get summary statistics for prices"""
    query = (
        select(
            Item.name.label("item_name"),
            Area.name.label("area_name"),
            func.count(ItemPrice.value).label("data_points"),
            func.avg(ItemPrice.value).label("average_price"),
            func.min(ItemPrice.value).label("min_price"),
            func.max(ItemPrice.value).label("max_price"),
            func.stddev(ItemPrice.value).label("price_std_dev"),
            ItemPrice.currency,
        )
        .join(Item, Item.id == ItemPrice.item_id)
        .join(Area, Area.id == ItemPrice.area_id)
        .where(and_(ItemPrice.year >= year_start, ItemPrice.year <= year_end))
    )

    # Add filters
    if item:
        if item.isdigit():
            query = query.where(Item.fao_code == int(item))
        else:
            query = query.where(Item.name.ilike(f"%{item}%"))

    if area:
        if area.isdigit():
            query = query.where(Area.fao_code == int(area))
        else:
            query = query.where(Area.name.ilike(f"%{area}%"))

    query = query.group_by(Item.name, Area.name, ItemPrice.currency).order_by(
        Item.name, Area.name
    )

    results = db.execute(query).mappings().all()
    return {
        "between_years": f"{year_start} - {year_end}",
        "summary_statistics": list(results),
    }


@app.get("/analysis/search-items")
def search_items(
    q: str = Query(..., description="Search query for item names"),
    limit: int = Query(10, description="Number of results"),
    db: Session = Depends(get_db),
):
    """Search for food items/commodities"""
    query = (
        select(
            Item.fao_code,
            Item.name,
            Item.cpc_code,
            func.count(ItemPrice.id).label("price_records"),
        )
        .outerjoin(ItemPrice, Item.id == ItemPrice.item_id)
        .where(Item.name.ilike(f"%{q}%"))
        .group_by(Item.fao_code, Item.name, Item.cpc_code)
        .order_by(desc(func.count(ItemPrice.id)))
        .limit(limit)
    )

    results = db.execute(query).mappings().all()
    return {"items": list(results)}


@app.get("/analysis/search-areas")
def search_areas(
    q: str = Query(..., description="Search query for area/country names"),
    limit: int = Query(10, description="Number of results"),
    db: Session = Depends(get_db),
):
    """Search for countries/areas"""
    query = (
        select(
            Area.fao_code,
            Area.name,
            Area.m49_code,
            func.count(ItemPrice.id).label("price_records"),
        )
        .outerjoin(ItemPrice, Area.id == ItemPrice.area_id)
        .where(Area.name.ilike(f"%{q}%"))
        .group_by(Area.fao_code, Area.name, Area.m49_code)
        .order_by(desc(func.count(ItemPrice.id)))
        .limit(limit)
    )

    results = db.execute(query).mappings().all()
    return {"areas": list(results)}


# Make it runnable with: python -m api
if __name__ == "__main__":
    import uvicorn
    import signal
    import sys

    def signal_handler(sig, frame):
        print("\nShutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    uvicorn.run("api.__main__:app", host="localhost", port=8000, reload=True)
