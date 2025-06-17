from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, text, String, Integer, Float, SmallInteger
from typing import Optional, Union, Dict, List
from fao.src.core.cache import cache_result
from fao.src.core import settings
from fao.src.db.database import get_db
from fao.src.db.pipelines.reporter_country_codes.reporter_country_codes_model import ReporterCountryCodes
import math
from datetime import datetime

router = APIRouter(
    prefix="/reporter_country_codes",
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
@cache_result(prefix="reporter_country_codes", ttl=86400, exclude_params=["response", "db"])
def get_reporter_country_codes(
    response: Response,
    limit: int = Query(100, le=1000, ge=1, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    # Dynamic column filters based on model
    reporter_country_code: Optional[str] = Query(None, description="Filter by reporter country code (partial match)"),
    reporter_country_code_exact: Optional[str] = Query(None, description="Filter by exact reporter country code"),
    reporter_countries: Optional[str] = Query(None, description="Filter by reporter countries (partial match)"),
    reporter_countries_exact: Optional[str] = Query(None, description="Filter by exact reporter countries"),
    reporter_country_code_m49: Optional[str] = Query(None, description="Filter by reporter country code m49 (partial match)"),
    reporter_country_code_m49_exact: Optional[str] = Query(None, description="Filter by exact reporter country code m49"),
    source_dataset: Optional[str] = Query(None, description="Filter by source dataset (partial match)"),
    source_dataset_exact: Optional[str] = Query(None, description="Filter by exact source dataset"),
    include_all_reference_columns: bool = Query(False, description="Include all columns from reference tables"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to return"),
    sort: Optional[str] = Query(None, description="Sort fields (use - prefix for descending, e.g., 'year,-value')"),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get reporter country codes data with filters and pagination.
    
    ## Pagination
    - Use `limit` and `offset` for page-based navigation
    - Response includes pagination metadata and total count
    - Link headers provided for easy navigation
    
    ## Filtering
    
    Dataset-specific filters:
    - reporter_country_code: Partial match (case-insensitive)
    - reporter_country_code_exact: Exact match
    - reporter_countries: Partial match (case-insensitive)
    - reporter_countries_exact: Exact match
    - reporter_country_code_m49: Partial match (case-insensitive)
    - reporter_country_code_m49_exact: Exact match
    - source_dataset: Partial match (case-insensitive)
    - source_dataset_exact: Exact match
    
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
    for col in ReporterCountryCodes.__table__.columns:
        if col.name not in ['created_at', 'updated_at']:
            column_map[col.name] = col
    
    
    # Now build columns list in the requested order
    if requested_fields:
        # Add columns in the order specified by the user
        for field_name in requested_fields:
            if field_name in column_map:
                columns.append(column_map[field_name])
            # If id is requested, include it even though we normally exclude it
            elif field_name == 'id' and hasattr(ReporterCountryCodes, 'id'):
                columns.append(ReporterCountryCodes.id)
    else:
        # No specific fields requested, use all available columns in default order
        for col in ReporterCountryCodes.__table__.columns:
            if col.name not in ['created_at', 'updated_at']:
                columns.append(col)
        
    
    # Build base query
    query = select(*columns).select_from(ReporterCountryCodes)
    
    
    # Build filter conditions for both main query and count query
    conditions = []
    
    # Apply foreign key filters
    
    # Apply dataset-specific column filters
    if reporter_country_code is not None:
        conditions.append(ReporterCountryCodes.reporter_country_code.ilike("%" + reporter_country_code + "%"))
    if reporter_country_code_exact is not None:
        conditions.append(ReporterCountryCodes.reporter_country_code == reporter_country_code_exact)
    if reporter_countries is not None:
        conditions.append(ReporterCountryCodes.reporter_countries.ilike("%" + reporter_countries + "%"))
    if reporter_countries_exact is not None:
        conditions.append(ReporterCountryCodes.reporter_countries == reporter_countries_exact)
    if reporter_country_code_m49 is not None:
        conditions.append(ReporterCountryCodes.reporter_country_code_m49.ilike("%" + reporter_country_code_m49 + "%"))
    if reporter_country_code_m49_exact is not None:
        conditions.append(ReporterCountryCodes.reporter_country_code_m49 == reporter_country_code_m49_exact)
    if source_dataset is not None:
        conditions.append(ReporterCountryCodes.source_dataset.ilike("%" + source_dataset + "%"))
    if source_dataset_exact is not None:
        conditions.append(ReporterCountryCodes.source_dataset == source_dataset_exact)
    
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
                    if hasattr(ReporterCountryCodes, field_name):
                        order_by_clauses.append(getattr(ReporterCountryCodes, field_name).desc())
                else:
                    # Ascending order
                    if hasattr(ReporterCountryCodes, sort_field):
                        order_by_clauses.append(getattr(ReporterCountryCodes, sort_field))
        
        if order_by_clauses:
            query = query.order_by(*order_by_clauses)
    else:
        # Default ordering by ID for consistent pagination
        query = query.order_by(ReporterCountryCodes.id)
    
    # Get total count with filters applied
    count_query = select(func.count()).select_from(ReporterCountryCodes)
    
    
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
    base_url = str(router.url_path_for('get_reporter_country_codes'))
    
    # Collect all query parameters
    all_params = {
        'limit': limit,
        'offset': offset,
        'reporter_country_code': reporter_country_code,
        'reporter_country_code_exact': reporter_country_code_exact,
        'reporter_countries': reporter_countries,
        'reporter_countries_exact': reporter_countries_exact,
        'reporter_country_code_m49': reporter_country_code_m49,
        'reporter_country_code_m49_exact': reporter_country_code_m49_exact,
        'source_dataset': source_dataset,
        'source_dataset_exact': source_dataset_exact,
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
