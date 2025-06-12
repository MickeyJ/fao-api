from pathlib import Path
import numpy as np
from typing import List, Optional
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, select, and_, or_, func, literal
from sqlalchemy.orm import aliased
from pydantic import BaseModel

# Correct imports following project patterns
from fao.src.db.database import get_db
from fao.src.core import settings
from fao.src.core.validation import is_valid_item_code, is_valid_element_code, is_valid_area_code, is_valid_year_range
from fao.src.core.exceptions import (
    invalid_parameter,
    invalid_item_code,
    invalid_element_code,
    invalid_area_code,
    missing_parameter,
    no_data_found,
)
from fao.src.db.pipelines.exchange_rate.exchange_rate_model import ExchangeRate
from fao.src.db.pipelines.item_codes.item_codes_model import ItemCodes
from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags
from fao.src.db.pipelines.prices.prices_model import Prices


def calculate_price_correlation(time_series, current_metrics):
    # Need at least 2 data points
    if len(time_series) < 2:
        return {
            "correlation": None,
            "correlation_based_integration": "insufficient_data",
            "ratio_based_integration": current_metrics["integration_level"],
        }

    # Calculate year-over-year returns
    returns1 = []
    returns2 = []

    for i in range(1, len(time_series)):
        return1 = (time_series[i]["price1"] - time_series[i - 1]["price1"]) / time_series[i - 1]["price1"]
        return2 = (time_series[i]["price2"] - time_series[i - 1]["price2"]) / time_series[i - 1]["price2"]
        returns1.append(return1)
        returns2.append(return2)

    # Calculate Pearson correlation
    correlation = np.corrcoef(returns1, returns2)[0, 1]

    # Handle NaN case (when all values are identical)
    if np.isnan(correlation):
        correlation = 0.0

    # Determine integration level based on correlation
    if correlation > 0.67:
        correlation_integration = "high"
    elif correlation > 0.33:
        correlation_integration = "moderate"
    else:
        correlation_integration = "none"

    return {
        "correlation": round(float(correlation), 3),  # Convert numpy float to Python float
        "correlation_based_integration": correlation_integration,
        "ratio_based_integration": current_metrics["integration_level"],
    }


def load_sql(filename: str) -> str:
    """Load SQL query from file"""
    sql_path = Path(__file__).parent / "sql" / filename
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")
    return sql_path.read_text()


router = APIRouter(prefix=f"/{settings.api_version_prefix}/market-integration", tags=["prices", "analytics", "custom"])


class MarketIntegrationPair(BaseModel):
    area_1_code: str
    area_1_name: str
    area_2_code: str
    area_2_name: str
    correlation: float
    data_points: int
    integration_level: str


class MarketIntegrationResponse(BaseModel):
    item: dict
    parameters: dict
    integration_pairs: List[MarketIntegrationPair]
    summary: dict


# "flag": "A",
# "description": "Official figure",
# "record_count": 837045,
# "percentage": 66.34

# "element_code": "5530",
# "element": "Producer Price (LCU/tonne)",
# "record_count": 512874

# "element_code": "5532",
# "element": "Producer Price (USD/tonne)",
# "record_count": 162702

PRICE_ELEMENT_CODE = "5530"
START_YEAR = 2005


@router.get("/correlations")
def get_market_integration(
    item_code: str = Query(..., description="FAO item code"),
    element_code: str = Query(PRICE_ELEMENT_CODE, description="Element code for price data"),
    year_start: int = Query(START_YEAR, description="Start year"),
    area_codes: Optional[List[str]] = Query(None, description="Specific countries to analyze"),
    db: Session = Depends(get_db),
):
    """
    Calculate market integration (price correlations) between countries for a commodity.

    High correlation (>0.8) indicates integrated markets where prices move together.
    Low correlation (<0.5) suggests isolated markets with independent price movements.
    """

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Item Code validation
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    if not item_code:
        raise missing_parameter("item_code")

    if not is_valid_item_code(item_code, db):
        raise invalid_item_code(item_code)

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Element Code validation
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    if not element_code:
        raise missing_parameter("element_code")

    if element_code and not is_valid_element_code(element_code, db):
        raise invalid_element_code(element_code)

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Area Code validation
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    if not area_codes:
        raise missing_parameter("area_codes")

    if len(area_codes) > 4:
        raise invalid_parameter(
            param="area_codes", value=f"{len(area_codes)} items", reason="maximum 4 area codes allowed"
        )

    for area_code in area_codes:
        if area_code and not is_valid_area_code(area_code, db):
            raise invalid_area_code(area_code)

    # Load SQL from file
    market_integration_query = load_sql("market_integration_USD.sql")

    if element_code == "5530":  # USD prices
        market_integration_query = load_sql("market_integration_LCU.sql")

    # Execute with parameters
    results = (
        db.execute(
            text(market_integration_query),
            {
                "item_code": item_code,
                "element_code": element_code,
                "start_year": year_start,
                "selected_area_codes": area_codes,
            },
        )
        .mappings()
        .all()
    )

    if not results:
        return {
            "item": {"code": item_code, "name": "Unknown"},
            "analysis_period": {
                "start_year": year_start,
                "end_year": None,
            },
            "countries_analyzed": len(area_codes),
            "comparisons_count": 0,
            "comparisons": [],
        }

    comparisons = []
    for row in results:

        metrics = {
            "years_compared": row["years_compared"],
            "avg_ratio": float(row["avg_ratio"]),
            "volatility": float(row["ratio_volatility"]),
            "min_ratio": float(row["min_ratio"]),
            "max_ratio": float(row["max_ratio"]),
            "integration_level": row["integration_level"],
        }

        comparisons.append(
            {
                "country_pair": {
                    "country1": {
                        "area_id": row["country1_id"],
                        "area_code": row["country1_code"],
                        "area_name": row["country1"],
                    },
                    "country2": {
                        "area_id": row["country2_id"],
                        "area_code": row["country2_code"],
                        "area_name": row["country2"],
                    },
                },
                "metrics": metrics,
                "calculated_metrics": calculate_price_correlation(row["time_series"], metrics),
                "time_series": row["time_series"],  # Already JSON from query
            }
        )

    # Get item details
    item_info = db.query(ItemCodes).filter(ItemCodes.item_code == item_code).first()

    return {
        "element_code": element_code,
        "item": {"code": item_code, "name": item_info.item if item_info else "Unknown"},
        "analysis_period": {
            "start_year": year_start,
            "end_year": max(max(point["year"] for point in comp["time_series"]) for comp in comparisons),
        },
        "countries_analyzed": len(area_codes),
        "comparisons_count": len(comparisons),
        "comparisons": comparisons,
    }


@router.get("/comparison")
def get_multi_line_price_trends(
    item_code: str = Query(None, description="Item FAO code (2-4 digits)"),
    area_codes: List[str] = Query(None, description="List of up to 5 area FAO codes"),
    element_code: str = Query(PRICE_ELEMENT_CODE, description="Element code for price data"),
    year_start: int = Query(1990, description="Start year"),
    year_end: int = Query(2023, description="End year"),
    db: Session = Depends(get_db),
):
    """
    Get price trend data for multi-line chart visualization
    Returns data optimized for D3.js multi-line charts
    """
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Item Code validation
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    if not item_code:
        raise missing_parameter("item_code")

    if not is_valid_item_code(item_code, db):
        raise invalid_item_code(item_code)

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Area Code validation
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    if not area_codes:
        raise missing_parameter("area_codes")

    if len(area_codes) > 5:
        raise invalid_parameter(
            param="area_codes", value=f"{len(area_codes)} items", reason="maximum 5 area codes allowed"
        )

    for area_code in area_codes:
        if area_code and not is_valid_area_code(area_code, db):
            raise invalid_area_code(area_code)

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Element Code validation
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    if not element_code:
        raise missing_parameter("element_code")

    if element_code and not is_valid_element_code(element_code, db):
        raise invalid_element_code(element_code)

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Year validation
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    if not is_valid_year_range(year_start, year_end):
        raise invalid_parameter(
            param="year_range", value=f"{year_start}-{year_end}", reason="start year must be before end year"
        )

    # Build the query based on element code
    if element_code == "5530":  # LCU prices need conversion
        # Subquery to get exchange rate area_codes
        exchange_area = aliased(AreaCodes)

        query = (
            select(
                AreaCodes.id.label("area_id"),
                AreaCodes.area.label("area_name"),
                AreaCodes.area_code.label("area_code"),
                Prices.year,
                (Prices.value / ExchangeRate.value).label("price"),  # Convert LCU to USD
                literal("USD").label("unit"),  # Converted to USD
                ItemCodes.item.label("item_name"),
            )
            .join(ItemCodes, ItemCodes.id == Prices.item_code_id)
            .join(AreaCodes, AreaCodes.id == Prices.area_code_id)
            .join(Elements, Elements.id == Prices.element_code_id)
            .join(Flags, Flags.id == Prices.flag_id)
            # Join exchange rate via area_code string matching
            .join(exchange_area, exchange_area.area_code == AreaCodes.area_code)
            .join(
                ExchangeRate,
                and_(
                    ExchangeRate.area_code_id == exchange_area.id,
                    ExchangeRate.year == Prices.year,
                    ExchangeRate.months_code == "7021",  # Annual rates
                    ExchangeRate.element_code_id
                    == select(Elements.id).where(Elements.element_code == "LCU").scalar_subquery(),
                ),
            )
            .where(
                and_(
                    Prices.year >= year_start,
                    Prices.year <= year_end,
                    ItemCodes.item_code == str(item_code),
                    Elements.element_code == element_code,
                    Flags.flag == "A",
                    Prices.months_code == "7021",  # Annual prices only
                    ExchangeRate.value > 0,  # Valid exchange rates
                )
            )
        )
    else:  # USD prices (5532) - original query
        query = (
            select(
                AreaCodes.id.label("area_id"),
                AreaCodes.area.label("area_name"),
                AreaCodes.area_code.label("area_code"),
                Prices.year,
                Prices.value.label("price"),
                Prices.unit,
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
                    Elements.element_code == element_code,
                    Flags.flag == "A",
                    Prices.months_code == "7021",  # Annual prices only
                )
            )
        )

    # Filter by area_codes (FAO codes) - same for both
    area_conditions = []
    for area_code in area_codes:
        area_conditions.append(AreaCodes.area_code == str(area_code))

    query = query.where(or_(*area_conditions))

    # Order by area and year for clean data structure
    query = query.order_by(AreaCodes.area, Prices.year)

    # Execute query
    results = db.execute(query).mappings().all()

    if not results:
        raise no_data_found(
            dataset="prices",
            filters={
                "item_code": item_code,
                "area_codes": area_codes,
                "element_code": element_code,
                "year_range": f"{year_start}-{year_end}",
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
                "area_id": row["area_id"],
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
            "element_code": element_code,
            "requested_areas": area_codes,
            "year_start": year_start,
            "year_end": year_end,
        },
        "lines": lines_data,
        "summary": summary,
        "currencies": list(units),  # Will be units for now
        "quantities": "Prices are likely in USD per metric ton",
        "note": "",
    }


@router.get("/items")
def get_all_items(
    element_code: str = Query(PRICE_ELEMENT_CODE, description="Element code for price data"),
    db: Session = Depends(get_db),
):
    """Get all food items that have price data"""

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Element Code validation
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    if not element_code:
        raise missing_parameter("element_code")

    if element_code and not is_valid_element_code(element_code, db):
        raise invalid_element_code(element_code)

    query = (
        select(
            ItemCodes.id,
            ItemCodes.item.label("name"),
            ItemCodes.item_code.label("item_code"),
            ItemCodes.item_code_cpc.label("cpc_code"),
            func.count(func.distinct(Prices.id)).label("price_points"),
            func.count(func.distinct(Prices.area_code_id)).label("countries_with_data"),
            func.count(func.distinct(Prices.year)).label("years_with_data"),
            func.min(Prices.year).label("earliest_year"),
            func.max(Prices.year).label("latest_year"),
            # Average data points per country (indicates data density)
            (func.count(Prices.id) / func.count(func.distinct(Prices.area_code_id))).label("avg_points_per_country"),
        )
        .join(Prices, ItemCodes.id == Prices.item_code_id)
        .join(Elements, Elements.id == Prices.element_code_id)
        .join(Flags, Flags.id == Prices.flag_id)
        .where(
            and_(
                Elements.element_code == element_code,  # '5532' for producer prices
                ItemCodes.source_dataset == "prices",
                Flags.flag == "A",
                Prices.year >= 1990,  # Recent data only
            )
        )
        .group_by(ItemCodes.id, ItemCodes.item, ItemCodes.item_code, ItemCodes.item_code_cpc)
        .having(
            and_(
                func.count(func.distinct(Prices.area_code_id)) >= 10,  # At least 10 countries
                func.count(func.distinct(Prices.year)) >= 5,  # At least 5 years of data
            )
        )
        .order_by(
            func.count(func.distinct(Prices.area_code_id)).desc(),  # Most countries first
            func.count(func.distinct(Prices.year)).desc(),  # Then most years
            func.count(Prices.id).desc(),  # Then most data points
        )
    )

    results = db.execute(query).mappings().all()

    if not results:
        raise no_data_found(
            dataset="item_codes",
            filters={
                "element_code": element_code,
            },
        )

    return {"items": [dict(item) for item in results]}


@router.get("/available-countries")
def get_countries_with_price_data(
    item_code: str = Query(..., description="FAO item code"),
    start_year: int = Query(START_YEAR, description="Start year"),
    element_code: str = Query(PRICE_ELEMENT_CODE, description="Element code for price data"),
    db: Session = Depends(get_db),
):
    """
    Get list of countries that have price data for a specific item in the given time range.
    Useful for the frontend to show available options.
    """

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Item Code validation
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    if not item_code:
        raise missing_parameter("item_code")

    if not is_valid_item_code(item_code, db):
        raise invalid_item_code(item_code)

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Element Code validation
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    if not element_code:
        raise missing_parameter("element_code")

    if element_code and not is_valid_element_code(element_code, db):
        raise invalid_element_code(element_code)

    # Load SQL query
    query_sql = load_sql("available_countries_for_item.sql")

    params = {"item_code": item_code, "element_code": element_code, "start_year": 1990}

    results = db.execute(text(query_sql), params).mappings().all()

    return {
        "item_code": item_code,
        "start_year": start_year,
        "countries": [dict(row) for row in results],
        "total_countries": len(results),
    }
