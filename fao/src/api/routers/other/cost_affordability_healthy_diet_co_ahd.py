from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, text, String, Integer, Float, SmallInteger
from typing import Optional, Union, Dict, List
from fao.src.core.cache import cache_result
from fao.src.core import settings
from fao.src.db.database import get_db
from fao.src.db.pipelines.cost_affordability_healthy_diet_co_ahd.cost_affordability_healthy_diet_co_ahd_model import CostAffordabilityHealthyDietCoAhd
import math
from datetime import datetime
# Import core/reference tables for joins
from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes
from fao.src.db.pipelines.item_codes.item_codes_model import ItemCodes
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.releases.releases_model import Releases
from fao.src.db.pipelines.flags.flags_model import Flags

router = APIRouter(
    prefix="/cost_affordability_healthy_diet_co_ahd",
    responses={404: {"description": "Not found"}},
)

def create_pagination_links(base_url: str, total_count: int, limit: int, offset: int, params: dict) -> dict:
    """Generate pagination links for response headers"""
    links = {}
    total_pages = math.ceil(total_count / limit) if limit > 0 else 1
    current_page = (offset // limit) + 1 if limit > 0 else 1
    
    # Remove offset from params to rebuild
    query_params = {k: v for k, v in params.items() if k not in ['offset', 'limit'] and v is not None}
    
    # Helper to build URL
    def build_url(new_offset: int) -> str:
        params_str = "&".join([f"{k}={v}" for k, v in query_params.items()])
        return f"{base_url}?limit={limit}&offset={new_offset}" + (f"&{params_str}" if params_str else "")
    
    # First page
    links['first'] = build_url(0)
    
    # Last page
    last_offset = (total_pages - 1) * limit
    links['last'] = build_url(last_offset)
    
    # Next page (if not on last page)
    if current_page < total_pages:
        links['next'] = build_url(offset + limit)
    
    # Previous page (if not on first page)
    if current_page > 1:
        links['prev'] = build_url(max(0, offset - limit))
    
    return links

@router.get("/")
@cache_result(prefix="cost_affordability_healthy_diet_co_ahd", ttl=86400, exclude_params=["response", "db"])
def get_cost_affordability_healthy_diet_co_ahd(
    response: Response,
    limit: int = Query(100, le=1000, ge=1, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    area_code: Optional[str] = Query(None, description="Filter by area_codes code"),
    area: Optional[str] = Query(None, description="Filter by area_codes description"),
    item_code: Optional[str] = Query(None, description="Filter by item_codes code"),
    item: Optional[str] = Query(None, description="Filter by item_codes description"),
    element_code: Optional[str] = Query(None, description="Filter by elements code"),
    element: Optional[str] = Query(None, description="Filter by elements description"),
    release_code: Optional[str] = Query(None, description="Filter by releases code"),
    release: Optional[str] = Query(None, description="Filter by releases description"),
    flag: Optional[str] = Query(None, description="Filter by flags code"),
    description: Optional[str] = Query(None, description="Filter by flags description"),
    # Dynamic column filters based on model
    year_code: Optional[str] = Query(None, description="Filter by year code (partial match)"),
    year_code_exact: Optional[str] = Query(None, description="Filter by exact year code"),
    year: Optional[int] = Query(None, description="Filter by exact year"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    year_max: Optional[int] = Query(None, description="Maximum year"),
    unit: Optional[str] = Query(None, description="Filter by unit (partial match)"),
    unit_exact: Optional[str] = Query(None, description="Filter by exact unit"),
    value: Optional[Union[float, int]] = Query(None, description="Exact value"),
    value_min: Optional[Union[float, int]] = Query(None, description="Minimum value"),
    value_max: Optional[Union[float, int]] = Query(None, description="Maximum value"),
    include_all_reference_columns: bool = Query(False, description="Include all columns from reference tables"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to return"),
    sort: Optional[str] = Query(None, description="Sort fields (use - prefix for descending, e.g., 'year,-value')"),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get cost affordability healthy diet co ahd data with filters and pagination.
    
    ## Pagination
    - Use `limit` and `offset` for page-based navigation
    - Response includes pagination metadata and total count
    - Link headers provided for easy navigation
    
    ## Filtering
    - area_code: Filter by area_codes code
    - area: Filter by area_codes description (partial match)
    - item_code: Filter by item_codes code
    - item: Filter by item_codes description (partial match)
    - element_code: Filter by elements code
    - element: Filter by elements description (partial match)
    - release_code: Filter by releases code
    - release: Filter by releases description (partial match)
    - flag: Filter by flags code
    - description: Filter by flags description (partial match)
    
    Dataset-specific filters:
    - year_code: Partial match (case-insensitive)
    - year_code_exact: Exact match
    - year: Exact year
    - year_min/year_max: Year range
    - unit: Partial match (case-insensitive)
    - unit_exact: Exact match
    - value: Exact value
    - value_min/value_max: Value range
    
    ## Response Format
    - Returns paginated data with metadata
    - Total count included for client-side pagination
    - Links to first, last, next, and previous pages
    """
    
    # Build column list for select
    columns = []
    column_map = {}  # Map of field name to column object
    
    # Parse requested fields if specified (preserving order)
    requested_fields = [field.strip() for field in fields.split(',') if field.strip()] if fields else None
    requested_fields_set = set(requested_fields) if requested_fields else None
    
    # First, build a map of all available columns
    # Main table columns
    for col in CostAffordabilityHealthyDietCoAhd.__table__.columns:
        if col.name not in ['created_at', 'updated_at']:
            column_map[col.name] = col
    
    # Reference table columns
    if include_all_reference_columns:
        # Add all reference columns
        for col in AreaCodes.__table__.columns:
            if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                col_alias = "area_codes_" + col.name
                column_map[col_alias] = col.label(col_alias)
    else:
        # Just key columns
        col_alias = "area_codes_area_code"
        column_map[col_alias] = AreaCodes.area_code.label(col_alias)
        col_alias = "area_codes_area"
        column_map[col_alias] = AreaCodes.area.label(col_alias)
        col_alias = "area_codes_area_code_m49"
        column_map[col_alias] = AreaCodes.area_code_m49.label(col_alias)
    if include_all_reference_columns:
        # Add all reference columns
        for col in ItemCodes.__table__.columns:
            if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                col_alias = "item_codes_" + col.name
                column_map[col_alias] = col.label(col_alias)
    else:
        # Just key columns
        col_alias = "item_codes_item_code"
        column_map[col_alias] = ItemCodes.item_code.label(col_alias)
        col_alias = "item_codes_item"
        column_map[col_alias] = ItemCodes.item.label(col_alias)
        col_alias = "item_codes_item_code_cpc"
        column_map[col_alias] = ItemCodes.item_code_cpc.label(col_alias)
        col_alias = "item_codes_item_code_fbs"
        column_map[col_alias] = ItemCodes.item_code_fbs.label(col_alias)
        col_alias = "item_codes_item_code_sdg"
        column_map[col_alias] = ItemCodes.item_code_sdg.label(col_alias)
    if include_all_reference_columns:
        # Add all reference columns
        for col in Elements.__table__.columns:
            if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                col_alias = "elements_" + col.name
                column_map[col_alias] = col.label(col_alias)
    else:
        # Just key columns
        col_alias = "elements_element_code"
        column_map[col_alias] = Elements.element_code.label(col_alias)
        col_alias = "elements_element"
        column_map[col_alias] = Elements.element.label(col_alias)
    if include_all_reference_columns:
        # Add all reference columns
        for col in Releases.__table__.columns:
            if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                col_alias = "releases_" + col.name
                column_map[col_alias] = col.label(col_alias)
    else:
        # Just key columns
        col_alias = "releases_release_code"
        column_map[col_alias] = Releases.release_code.label(col_alias)
        col_alias = "releases_release"
        column_map[col_alias] = Releases.release.label(col_alias)
    if include_all_reference_columns:
        # Add all reference columns
        for col in Flags.__table__.columns:
            if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                col_alias = "flags_" + col.name
                column_map[col_alias] = col.label(col_alias)
    else:
        # Just key columns
        col_alias = "flags_flag"
        column_map[col_alias] = Flags.flag.label(col_alias)
        col_alias = "flags_description"
        column_map[col_alias] = Flags.description.label(col_alias)
    
    # Now build columns list in the requested order
    if requested_fields:
        # Add columns in the order specified by the user
        for field_name in requested_fields:
            if field_name in column_map:
                columns.append(column_map[field_name])
            # If id is requested, include it even though we normally exclude it
            elif field_name == 'id' and hasattr(CostAffordabilityHealthyDietCoAhd, 'id'):
                columns.append(CostAffordabilityHealthyDietCoAhd.id)
    else:
        # No specific fields requested, use all available columns in default order
        for col in CostAffordabilityHealthyDietCoAhd.__table__.columns:
            if col.name not in ['created_at', 'updated_at']:
                columns.append(col)
        
        # Add reference columns in default order
        if include_all_reference_columns:
            for col in AreaCodes.__table__.columns:
                if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                    columns.append(col.label("area_codes_" + col.name))
        else:
            columns.append(AreaCodes.area_code.label("area_codes_area_code"))
            columns.append(AreaCodes.area.label("area_codes_area"))
            columns.append(AreaCodes.area_code_m49.label("area_codes_area_code_m49"))
        if include_all_reference_columns:
            for col in ItemCodes.__table__.columns:
                if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                    columns.append(col.label("item_codes_" + col.name))
        else:
            columns.append(ItemCodes.item_code.label("item_codes_item_code"))
            columns.append(ItemCodes.item.label("item_codes_item"))
            columns.append(ItemCodes.item_code_cpc.label("item_codes_item_code_cpc"))
            columns.append(ItemCodes.item_code_fbs.label("item_codes_item_code_fbs"))
            columns.append(ItemCodes.item_code_sdg.label("item_codes_item_code_sdg"))
        if include_all_reference_columns:
            for col in Elements.__table__.columns:
                if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                    columns.append(col.label("elements_" + col.name))
        else:
            columns.append(Elements.element_code.label("elements_element_code"))
            columns.append(Elements.element.label("elements_element"))
        if include_all_reference_columns:
            for col in Releases.__table__.columns:
                if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                    columns.append(col.label("releases_" + col.name))
        else:
            columns.append(Releases.release_code.label("releases_release_code"))
            columns.append(Releases.release.label("releases_release"))
        if include_all_reference_columns:
            for col in Flags.__table__.columns:
                if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                    columns.append(col.label("flags_" + col.name))
        else:
            columns.append(Flags.flag.label("flags_flag"))
            columns.append(Flags.description.label("flags_description"))
    
    # Build base query
    query = select(*columns).select_from(CostAffordabilityHealthyDietCoAhd)
    
    # Add joins
    query = query.outerjoin(AreaCodes, CostAffordabilityHealthyDietCoAhd.area_code_id == AreaCodes.id)
    query = query.outerjoin(ItemCodes, CostAffordabilityHealthyDietCoAhd.item_code_id == ItemCodes.id)
    query = query.outerjoin(Elements, CostAffordabilityHealthyDietCoAhd.element_code_id == Elements.id)
    query = query.outerjoin(Releases, CostAffordabilityHealthyDietCoAhd.release_code_id == Releases.id)
    query = query.outerjoin(Flags, CostAffordabilityHealthyDietCoAhd.flag_id == Flags.id)
    
    # Build filter conditions for both main query and count query
    conditions = []
    
    # Apply foreign key filters
    if area_code:
        conditions.append(AreaCodes.area_code == area_code)
    if area:
        conditions.append(AreaCodes.area.ilike("%" + area + "%"))
    if item_code:
        conditions.append(ItemCodes.item_code == item_code)
    if item:
        conditions.append(ItemCodes.item.ilike("%" + item + "%"))
    if element_code:
        conditions.append(Elements.element_code == element_code)
    if element:
        conditions.append(Elements.element.ilike("%" + element + "%"))
    if release_code:
        conditions.append(Releases.release_code == release_code)
    if release:
        conditions.append(Releases.release.ilike("%" + release + "%"))
    if flag:
        conditions.append(Flags.flag == flag)
    if description:
        conditions.append(Flags.description.ilike("%" + description + "%"))
    
    # Apply dataset-specific column filters
    if year_code is not None:
        conditions.append(CostAffordabilityHealthyDietCoAhd.year_code.ilike("%" + year_code + "%"))
    if year_code_exact is not None:
        conditions.append(CostAffordabilityHealthyDietCoAhd.year_code == year_code_exact)
    if year is not None:
        conditions.append(CostAffordabilityHealthyDietCoAhd.year == year)
    if year_min is not None:
        conditions.append(CostAffordabilityHealthyDietCoAhd.year >= year_min)
    if year_max is not None:
        conditions.append(CostAffordabilityHealthyDietCoAhd.year <= year_max)
    if unit is not None:
        conditions.append(CostAffordabilityHealthyDietCoAhd.unit.ilike("%" + unit + "%"))
    if unit_exact is not None:
        conditions.append(CostAffordabilityHealthyDietCoAhd.unit == unit_exact)
    if value is not None:
        conditions.append(CostAffordabilityHealthyDietCoAhd.value == value)
    if value_min is not None:
        conditions.append(CostAffordabilityHealthyDietCoAhd.value >= value_min)
    if value_max is not None:
        conditions.append(CostAffordabilityHealthyDietCoAhd.value <= value_max)
    
    # Apply all conditions
    if conditions:
        query = query.where(*conditions)
    
    # Apply sorting if specified
    if sort:
        order_by_clauses = []
        for sort_field in sort.split(','):
            sort_field = sort_field.strip()
            if sort_field:  # Skip empty strings
                if sort_field.startswith('-'):
                    # Descending order
                    field_name = sort_field[1:].strip()
                    if hasattr(CostAffordabilityHealthyDietCoAhd, field_name):
                        order_by_clauses.append(getattr(CostAffordabilityHealthyDietCoAhd, field_name).desc())
                else:
                    # Ascending order
                    if hasattr(CostAffordabilityHealthyDietCoAhd, sort_field):
                        order_by_clauses.append(getattr(CostAffordabilityHealthyDietCoAhd, sort_field))
        
        if order_by_clauses:
            query = query.order_by(*order_by_clauses)
    else:
        # Default ordering by ID for consistent pagination
        query = query.order_by(CostAffordabilityHealthyDietCoAhd.id)
    
    # Get total count with filters applied
    count_query = select(func.count()).select_from(CostAffordabilityHealthyDietCoAhd)
    
    # Add joins to count query
    count_query = count_query.outerjoin(AreaCodes, CostAffordabilityHealthyDietCoAhd.area_code_id == AreaCodes.id)
    count_query = count_query.outerjoin(ItemCodes, CostAffordabilityHealthyDietCoAhd.item_code_id == ItemCodes.id)
    count_query = count_query.outerjoin(Elements, CostAffordabilityHealthyDietCoAhd.element_code_id == Elements.id)
    count_query = count_query.outerjoin(Releases, CostAffordabilityHealthyDietCoAhd.release_code_id == Releases.id)
    count_query = count_query.outerjoin(Flags, CostAffordabilityHealthyDietCoAhd.flag_id == Flags.id)
    
    # Apply same conditions to count query
    if conditions:
        count_query = count_query.where(*conditions)
    
    total_count = db.execute(count_query).scalar() or 0
    
    # Calculate pagination metadata
    total_pages = math.ceil(total_count / limit) if limit > 0 else 1
    current_page = (offset // limit) + 1 if limit > 0 else 1
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute query
    results = db.execute(query).mappings().all()
    
    # Convert results preserving field order
    ordered_data = []
    if requested_fields:
        # Preserve the exact order from the fields parameter
        for row in results:
            ordered_row = {}
            for field_name in requested_fields:
                if field_name in row:
                    ordered_row[field_name] = row[field_name]
                elif field_name == 'id' and 'id' in row:
                    ordered_row['id'] = row['id']
            ordered_data.append(ordered_row)
    else:
        # No specific order requested, use as-is
        ordered_data = [dict(row) for row in results]
    
    # Build pagination links
    base_url = str(router.url_path_for('get_cost_affordability_healthy_diet_co_ahd'))
    
    # Collect all query parameters
    all_params = {
        'limit': limit,
        'offset': offset,
        'area_code': area_code,
        'area': area,
        'item_code': item_code,
        'item': item,
        'element_code': element_code,
        'element': element,
        'release_code': release_code,
        'release': release,
        'flag': flag,
        'description': description,
        'year_code': year_code,
        'year_code_exact': year_code_exact,
        'year': year,
        'year_min': year_min,
        'year_max': year_max,
        'unit': unit,
        'unit_exact': unit_exact,
        'value': value,
        'value_min': value_min,
        'value_max': value_max,
        'include_all_reference_columns': include_all_reference_columns,
        'fields': fields,
        'sort': sort,
    }
    
    links = create_pagination_links(base_url, total_count, limit, offset, all_params)
    
    # Set response headers
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["X-Total-Pages"] = str(total_pages)
    response.headers["X-Current-Page"] = str(current_page)
    response.headers["X-Per-Page"] = str(limit)
    
    # Build Link header
    link_parts = []
    for rel, url in links.items():
        link_parts.append(f'<{url}>; rel="{rel}"')
    if link_parts:
        response.headers["Link"] = ", ".join(link_parts)
    
    # Return response with pagination metadata
    return {
        "data": ordered_data,
        "pagination": {
            "total": total_count,
            "total_pages": total_pages,
            "current_page": current_page,
            "per_page": limit,
            "from": offset + 1 if results else 0,
            "to": offset + len(results),
            "has_next": current_page < total_pages,
            "has_prev": current_page > 1,
        },
        "links": links,
        "_meta": {
            "generated_at": datetime.utcnow().isoformat(),
            "filters_applied": sum(1 for v in all_params.values() if v is not None and v != '' and v != False),
        }
    }


# Keep all existing metadata endpoints unchanged...
# Metadata endpoints for understanding the dataset

@router.get("/areas")
@cache_result(prefix="cost_affordability_healthy_diet_co_ahd:areas", ttl=604800)
def get_available_areas(db: Session = Depends(get_db)):
    """Get all areas with data in this dataset"""
    query = (
        select(
            AreaCodes.area_code,
            AreaCodes.area,
            AreaCodes.area_code_m49,
        )
        .where(AreaCodes.source_dataset == 'cost_affordability_healthy_diet_co_ahd')
        .order_by(AreaCodes.area_code)
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "cost_affordability_healthy_diet_co_ahd",
        "total_areas": len(results),
        "areas": [
            {
                "area_code": r.area_code,
                "area": r.area,
                "area_code_m49": r.area_code_m49,
            }
            for r in results
        ]
    }



@router.get("/items")
@cache_result(prefix="cost_affordability_healthy_diet_co_ahd:items", ttl=604800)
def get_available_items(db: Session = Depends(get_db)):
    """Get all items available in this dataset with record counts"""
    query = (
        select(
            ItemCodes.item_code,
            ItemCodes.item,
            ItemCodes.item_code_cpc,
            ItemCodes.item_code_fbs,
            ItemCodes.item_code_sdg,
        )
        .where(ItemCodes.source_dataset == 'cost_affordability_healthy_diet_co_ahd')
        .order_by(ItemCodes.item_code)
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "cost_affordability_healthy_diet_co_ahd",
        "total_items": len(results),
        "items": [
            {
                "item_code": r.item_code,
                "item": r.item,
                "item_code_cpc": r.item_code_cpc,
                "item_code_fbs": r.item_code_fbs,
                "item_code_sdg": r.item_code_sdg,
            }
            for r in results
        ]
    }






@router.get("/elements")
@cache_result(prefix="cost_affordability_healthy_diet_co_ahd:elements", ttl=604800)
def get_available_elements(db: Session = Depends(get_db)):
    """Get all elements (measures/indicators) in this dataset"""
    query = (
        select(
            Elements.element_code,  
            Elements.element
        )
        .where(Elements.source_dataset == 'cost_affordability_healthy_diet_co_ahd')
        .order_by(Elements.element_code)
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "cost_affordability_healthy_diet_co_ahd",
        "total_elements": len(results),
        "elements": [
            {
                "element_code": r.element_code,
                "element": r.element,
            }
            for r in results
        ]
    }






@router.get("/releases")
@cache_result(prefix="cost_affordability_healthy_diet_co_ahd:releases", ttl=604800)
def get_available_releases(db: Session = Depends(get_db)):
    """Get all releases in this dataset"""
    query = (
        select(
            Releases.release_code,
            Releases.release
        )
        .where(Releases.source_dataset == 'cost_affordability_healthy_diet_co_ahd')
        .order_by(Releases.release_code)
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "cost_affordability_healthy_diet_co_ahd",
        "total_releases": len(results),
        "releases": [
            {
                "release_code": r.release_code,
                "release": r.release
            }
            for r in results
        ]
    }



@router.get("/flags")
@cache_result(prefix="cost_affordability_healthy_diet_co_ahd:flags", ttl=604800)
def get_data_quality_summary(db: Session = Depends(get_db)):
    """Get data quality flag distribution for this dataset"""
    query = (
        select(
            Flags.flag,
            Flags.description,
            func.count(CostAffordabilityHealthyDietCoAhd.id).label('record_count')
        )
        .join(CostAffordabilityHealthyDietCoAhd, Flags.id == CostAffordabilityHealthyDietCoAhd.flag_id)
        .group_by(Flags.flag, Flags.description)
        .order_by(func.count(CostAffordabilityHealthyDietCoAhd.id).desc())
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "cost_affordability_healthy_diet_co_ahd",
        "total_records": sum(r.record_count for r in results),
        "flag_distribution": [
            {
                "flag": r.flag,
                "description": r.description,
                "record_count": r.record_count,
                "percentage": round(r.record_count / sum(r2.record_count for r2 in results) * 100, 2)
            }
            for r in results
        ]
    }


@router.get("/years")
@cache_result(prefix="cost_affordability_healthy_diet_co_ahd:years", ttl=604800)
def get_temporal_coverage(db: Session = Depends(get_db)):
    """Get temporal coverage information for this dataset"""
    # Get year range and counts
    query = (
        select(
            CostAffordabilityHealthyDietCoAhd.year,
            func.count(CostAffordabilityHealthyDietCoAhd.id).label('record_count')
        )
        .group_by(CostAffordabilityHealthyDietCoAhd.year)
        .order_by(CostAffordabilityHealthyDietCoAhd.year)
    )
    
    results = db.execute(query).all()
    years_data = [{"year": r.year, "record_count": r.record_count} for r in results]
    
    if not years_data:
        return {"dataset": "cost_affordability_healthy_diet_co_ahd", "message": "No temporal data available"}
    
    return {
        "dataset": "cost_affordability_healthy_diet_co_ahd",
        "earliest_year": min(r["year"] for r in years_data),
        "latest_year": max(r["year"] for r in years_data),
        "total_years": len(years_data),
        "total_records": sum(r["record_count"] for r in years_data),
        "years": years_data
    }

@router.get("/summary")
@cache_result(prefix="cost_affordability_healthy_diet_co_ahd:summary", ttl=604800)
def get_dataset_summary(db: Session = Depends(get_db)):
    """Get comprehensive summary of this dataset"""
    total_records = db.query(func.count(CostAffordabilityHealthyDietCoAhd.id)).scalar()
    
    summary = {
        "dataset": "cost_affordability_healthy_diet_co_ahd",
        "total_records": total_records,
        "foreign_keys": [
            "area_codes",
            "item_codes",
            "elements",
            "releases",
            "flags",
        ]
    }
    
    summary["unique_areas"] = db.query(func.count(func.distinct(CostAffordabilityHealthyDietCoAhd.area_code_id))).scalar()
    summary["unique_items"] = db.query(func.count(func.distinct(CostAffordabilityHealthyDietCoAhd.item_code_id))).scalar()
    summary["unique_elements"] = db.query(func.count(func.distinct(CostAffordabilityHealthyDietCoAhd.element_code_id))).scalar()
    summary["unique_releases"] = db.query(func.count(func.distinct(CostAffordabilityHealthyDietCoAhd.release_code_id))).scalar()
    summary["unique_flags"] = db.query(func.count(func.distinct(CostAffordabilityHealthyDietCoAhd.flag_id))).scalar()
    
    return summary
