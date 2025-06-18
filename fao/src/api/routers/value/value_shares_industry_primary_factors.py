from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, text, String, Integer, Float, SmallInteger
from typing import Optional, Union, Dict, List
from fao.src.core.cache import cache_result
from fao.src.core import settings
from fao.src.db.database import get_db
from fao.src.db.pipelines.value_shares_industry_primary_factors.value_shares_industry_primary_factors_model import ValueSharesIndustryPrimaryFactors
import math
from datetime import datetime
# Import core/reference tables for joins
from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

router = APIRouter(
    prefix="/value_shares_industry_primary_factors",
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
@cache_result(prefix="value_shares_industry_primary_factors", ttl=86400, exclude_params=["response", "db"])
def get_value_shares_industry_primary_factors(
    response: Response,
    limit: int = Query(100, le=1000, ge=1, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    area_code: Optional[str] = Query(None, description="Filter by area_codes code"),
    area: Optional[str] = Query(None, description="Filter by area_codes description"),
    element_code: Optional[str] = Query(None, description="Filter by elements code"),
    element: Optional[str] = Query(None, description="Filter by elements description"),
    flag: Optional[str] = Query(None, description="Filter by flags code"),
    description: Optional[str] = Query(None, description="Filter by flags description"),
    # Dynamic column filters based on model
    food_value_code: Optional[str] = Query(None, description="Filter by food value code (partial match)"),
    food_value_code_exact: Optional[str] = Query(None, description="Filter by exact food value code"),
    food_value: Optional[str] = Query(None, description="Filter by food value (partial match)"),
    food_value_exact: Optional[str] = Query(None, description="Filter by exact food value"),
    industry_code: Optional[str] = Query(None, description="Filter by industry code (partial match)"),
    industry_code_exact: Optional[str] = Query(None, description="Filter by exact industry code"),
    industry: Optional[str] = Query(None, description="Filter by industry (partial match)"),
    industry_exact: Optional[str] = Query(None, description="Filter by exact industry"),
    factor_code: Optional[str] = Query(None, description="Filter by factor code (partial match)"),
    factor_code_exact: Optional[str] = Query(None, description="Filter by exact factor code"),
    factor: Optional[str] = Query(None, description="Filter by factor (partial match)"),
    factor_exact: Optional[str] = Query(None, description="Filter by exact factor"),
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
    Get value shares industry primary factors data with filters and pagination.
    
    ## Pagination
    - Use `limit` and `offset` for page-based navigation
    - Response includes pagination metadata and total count
    - Link headers provided for easy navigation
    
    ## Filtering
    - area_code: Filter by area_codes code
    - area: Filter by area_codes description (partial match)
    - element_code: Filter by elements code
    - element: Filter by elements description (partial match)
    - flag: Filter by flags code
    - description: Filter by flags description (partial match)
    
    Dataset-specific filters:
    - food_value_code: Partial match (case-insensitive)
    - food_value_code_exact: Exact match
    - food_value: Partial match (case-insensitive)
    - food_value_exact: Exact match
    - industry_code: Partial match (case-insensitive)
    - industry_code_exact: Exact match
    - industry: Partial match (case-insensitive)
    - industry_exact: Exact match
    - factor_code: Partial match (case-insensitive)
    - factor_code_exact: Exact match
    - factor: Partial match (case-insensitive)
    - factor_exact: Exact match
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
    for col in ValueSharesIndustryPrimaryFactors.__table__.columns:
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
            elif field_name == 'id' and hasattr(ValueSharesIndustryPrimaryFactors, 'id'):
                columns.append(ValueSharesIndustryPrimaryFactors.id)
    else:
        # No specific fields requested, use all available columns in default order
        for col in ValueSharesIndustryPrimaryFactors.__table__.columns:
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
            for col in Elements.__table__.columns:
                if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                    columns.append(col.label("elements_" + col.name))
        else:
            columns.append(Elements.element_code.label("elements_element_code"))
            columns.append(Elements.element.label("elements_element"))
        if include_all_reference_columns:
            for col in Flags.__table__.columns:
                if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                    columns.append(col.label("flags_" + col.name))
        else:
            columns.append(Flags.flag.label("flags_flag"))
            columns.append(Flags.description.label("flags_description"))
    
    # Build base query
    query = select(*columns).select_from(ValueSharesIndustryPrimaryFactors)
    
    # Add joins
    query = query.outerjoin(AreaCodes, ValueSharesIndustryPrimaryFactors.area_code_id == AreaCodes.id)
    query = query.outerjoin(Elements, ValueSharesIndustryPrimaryFactors.element_code_id == Elements.id)
    query = query.outerjoin(Flags, ValueSharesIndustryPrimaryFactors.flag_id == Flags.id)
    
    # Build filter conditions for both main query and count query
    conditions = []
    
    # Apply foreign key filters
    if area_code:
        conditions.append(AreaCodes.area_code == area_code)
    if area:
        conditions.append(AreaCodes.area.ilike("%" + area + "%"))
    if element_code:
        conditions.append(Elements.element_code == element_code)
    if element:
        conditions.append(Elements.element.ilike("%" + element + "%"))
    if flag:
        conditions.append(Flags.flag == flag)
    if description:
        conditions.append(Flags.description.ilike("%" + description + "%"))
    
    # Apply dataset-specific column filters
    if food_value_code is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.food_value_code.ilike("%" + food_value_code + "%"))
    if food_value_code_exact is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.food_value_code == food_value_code_exact)
    if food_value is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.food_value.ilike("%" + food_value + "%"))
    if food_value_exact is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.food_value == food_value_exact)
    if industry_code is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.industry_code.ilike("%" + industry_code + "%"))
    if industry_code_exact is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.industry_code == industry_code_exact)
    if industry is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.industry.ilike("%" + industry + "%"))
    if industry_exact is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.industry == industry_exact)
    if factor_code is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.factor_code.ilike("%" + factor_code + "%"))
    if factor_code_exact is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.factor_code == factor_code_exact)
    if factor is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.factor.ilike("%" + factor + "%"))
    if factor_exact is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.factor == factor_exact)
    if year_code is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.year_code.ilike("%" + year_code + "%"))
    if year_code_exact is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.year_code == year_code_exact)
    if year is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.year == year)
    if year_min is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.year >= year_min)
    if year_max is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.year <= year_max)
    if unit is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.unit.ilike("%" + unit + "%"))
    if unit_exact is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.unit == unit_exact)
    if value is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.value == value)
    if value_min is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.value >= value_min)
    if value_max is not None:
        conditions.append(ValueSharesIndustryPrimaryFactors.value <= value_max)
    
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
                    if hasattr(ValueSharesIndustryPrimaryFactors, field_name):
                        order_by_clauses.append(getattr(ValueSharesIndustryPrimaryFactors, field_name).desc())
                else:
                    # Ascending order
                    if hasattr(ValueSharesIndustryPrimaryFactors, sort_field):
                        order_by_clauses.append(getattr(ValueSharesIndustryPrimaryFactors, sort_field))
        
        if order_by_clauses:
            query = query.order_by(*order_by_clauses)
    else:
        # Default ordering by ID for consistent pagination
        query = query.order_by(ValueSharesIndustryPrimaryFactors.id)
    
    # Get total count with filters applied
    count_query = select(func.count()).select_from(ValueSharesIndustryPrimaryFactors)
    
    # Add joins to count query
    count_query = count_query.outerjoin(AreaCodes, ValueSharesIndustryPrimaryFactors.area_code_id == AreaCodes.id)
    count_query = count_query.outerjoin(Elements, ValueSharesIndustryPrimaryFactors.element_code_id == Elements.id)
    count_query = count_query.outerjoin(Flags, ValueSharesIndustryPrimaryFactors.flag_id == Flags.id)
    
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
    base_url = str(router.url_path_for('get_value_shares_industry_primary_factors'))
    
    # Collect all query parameters
    all_params = {
        'limit': limit,
        'offset': offset,
        'area_code': area_code,
        'area': area,
        'element_code': element_code,
        'element': element,
        'flag': flag,
        'description': description,
        'food_value_code': food_value_code,
        'food_value_code_exact': food_value_code_exact,
        'food_value': food_value,
        'food_value_exact': food_value_exact,
        'industry_code': industry_code,
        'industry_code_exact': industry_code_exact,
        'industry': industry,
        'industry_exact': industry_exact,
        'factor_code': factor_code,
        'factor_code_exact': factor_code_exact,
        'factor': factor,
        'factor_exact': factor_exact,
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
@cache_result(prefix="value_shares_industry_primary_factors:areas", ttl=604800)
def get_available_areas(db: Session = Depends(get_db)):
    """Get all areas with data in this dataset"""
    query = (
        select(
            AreaCodes.area_code,
            AreaCodes.area,
            AreaCodes.area_code_m49,
        )
        .where(AreaCodes.source_dataset == 'value_shares_industry_primary_factors')
        .order_by(AreaCodes.area_code)
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "value_shares_industry_primary_factors",
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





@router.get("/elements")
@cache_result(prefix="value_shares_industry_primary_factors:elements", ttl=604800)
def get_available_elements(db: Session = Depends(get_db)):
    """Get all elements (measures/indicators) in this dataset"""
    query = (
        select(
            Elements.element_code,  
            Elements.element
        )
        .where(Elements.source_dataset == 'value_shares_industry_primary_factors')
        .order_by(Elements.element_code)
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "value_shares_industry_primary_factors",
        "total_elements": len(results),
        "elements": [
            {
                "element_code": r.element_code,
                "element": r.element,
            }
            for r in results
        ]
    }





@router.get("/flags")
@cache_result(prefix="value_shares_industry_primary_factors:flags", ttl=604800)
def get_data_quality_summary(db: Session = Depends(get_db)):
    """Get data quality flag distribution for this dataset"""
    query = (
        select(
            Flags.flag,
            Flags.description,
            func.count(ValueSharesIndustryPrimaryFactors.id).label('record_count')
        )
        .join(ValueSharesIndustryPrimaryFactors, Flags.id == ValueSharesIndustryPrimaryFactors.flag_id)
        .group_by(Flags.flag, Flags.description)
        .order_by(func.count(ValueSharesIndustryPrimaryFactors.id).desc())
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "value_shares_industry_primary_factors",
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
@cache_result(prefix="value_shares_industry_primary_factors:years", ttl=604800)
def get_temporal_coverage(db: Session = Depends(get_db)):
    """Get temporal coverage information for this dataset"""
    # Get year range and counts
    query = (
        select(
            ValueSharesIndustryPrimaryFactors.year,
            func.count(ValueSharesIndustryPrimaryFactors.id).label('record_count')
        )
        .group_by(ValueSharesIndustryPrimaryFactors.year)
        .order_by(ValueSharesIndustryPrimaryFactors.year)
    )
    
    results = db.execute(query).all()
    years_data = [{"year": r.year, "record_count": r.record_count} for r in results]
    
    if not years_data:
        return {"dataset": "value_shares_industry_primary_factors", "message": "No temporal data available"}
    
    return {
        "dataset": "value_shares_industry_primary_factors",
        "earliest_year": min(r["year"] for r in years_data),
        "latest_year": max(r["year"] for r in years_data),
        "total_years": len(years_data),
        "total_records": sum(r["record_count"] for r in years_data),
        "years": years_data
    }

@router.get("/summary")
@cache_result(prefix="value_shares_industry_primary_factors:summary", ttl=604800)
def get_dataset_summary(db: Session = Depends(get_db)):
    """Get comprehensive summary of this dataset"""
    total_records = db.query(func.count(ValueSharesIndustryPrimaryFactors.id)).scalar()
    
    summary = {
        "dataset": "value_shares_industry_primary_factors",
        "total_records": total_records,
        "foreign_keys": [
            "area_codes",
            "elements",
            "flags",
        ]
    }
    
    summary["unique_areas"] = db.query(func.count(func.distinct(ValueSharesIndustryPrimaryFactors.area_code_id))).scalar()
    summary["unique_elements"] = db.query(func.count(func.distinct(ValueSharesIndustryPrimaryFactors.element_code_id))).scalar()
    summary["unique_flags"] = db.query(func.count(func.distinct(ValueSharesIndustryPrimaryFactors.flag_id))).scalar()
    
    return summary
