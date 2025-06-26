# templates/api_router.py.jinja2 (refactored main)
from fastapi import APIRouter, Depends, Query, HTTPException, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, and_, String
from typing import Optional, List, Union
from datetime import datetime

from fao.logger import logger
from fao.src.core.cache import cache_result
from fao.src.core import settings
from fao.src.db.database import get_db
from fao.src.db.pipelines.fertilizers_detailed_trade_matrix.fertilizers_detailed_trade_matrix_model import FertilizersDetailedTradeMatrix


from fao.src.db.pipelines.reporter_country_codes.reporter_country_codes_model import ReporterCountryCodes
from fao.src.db.pipelines.partner_country_codes.partner_country_codes_model import PartnerCountryCodes
from fao.src.db.pipelines.item_codes.item_codes_model import ItemCodes
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

# Import utilities
from fao.src.api.utils.dataset_router import DatasetRouterHandler
from .fertilizers_detailed_trade_matrix_config import FertilizersDetailedTradeMatrixConfig
from fao.src.api.utils.query_helpers import QueryBuilder, AggregationType
from fao.src.api.utils.response_helpers import PaginationBuilder, ResponseFormatter
from fao.src.api.utils.parameter_parsers import (
    parse_sort_parameter, 
    parse_fields_parameter,
    parse_aggregation_parameter
)

from fao.src.core.validation import (
    is_valid_sort_direction,
    is_valid_aggregation_function,
    validate_fields_exist,
    validate_model_has_columns,
    is_valid_element_code,
    is_valid_flag,
    is_valid_item_code,
    is_valid_partner_country_code,
    is_valid_reporter_country_code,
)

from fao.src.core.exceptions import (
    invalid_parameter,
    missing_parameter,
    incompatible_parameters,
    invalid_element_code,
    invalid_flag,
    invalid_item_code,
    invalid_partner_country_code,
    invalid_reporter_country_code,
)

router = APIRouter(
    prefix="/fertilizers_detailed_trade_matrix",
    responses={404: {"description": "Not found"}},
)


config = FertilizersDetailedTradeMatrixConfig()

@router.get("/", summary="Get fertilizers detailed trade matrix data")
async def get_fertilizers_detailed_trade_matrix_data(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    # Standard parameters
    limit: int = Query(100, ge=0, le=10000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),

    # Filter parameters
    reporter_country_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by reporter_country_code code (comma-separated for multiple)"),
    reporter_countries: Optional[str] = Query(None, description="Filter by reporter_countries description (partial match)"),
    partner_country_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by partner_country_code code (comma-separated for multiple)"),
    partner_countries: Optional[str] = Query(None, description="Filter by partner_countries description (partial match)"),
    item_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by item_code code (comma-separated for multiple)"),
    item: Optional[str] = Query(None, description="Filter by item description (partial match)"),
    element_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by element_code code (comma-separated for multiple)"),
    element: Optional[str] = Query(None, description="Filter by element description (partial match)"),
    flag: Optional[Union[str, List[str]]] = Query(None, description="Filter by flag code (comma-separated for multiple)"),
    description: Optional[str] = Query(None, description="Filter by description description (partial match)"),
    year_code: Optional[str] = Query(None, description="Filter by year code (partial match)"),
    year: Optional[int] = Query(None, description="Filter by exact year"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    year_max: Optional[int] = Query(None, description="Maximum year"),
    unit: Optional[str] = Query(None, description="Filter by unit (partial match)"),
    value: Optional[Union[float, int]] = Query(None, description="Exact value"),
    value_min: Optional[Union[float, int]] = Query(None, description="Minimum value"),
    value_max: Optional[Union[float, int]] = Query(None, description="Maximum value"),

    # Option parameters  
    fields: Optional[List[str]] = Query(None, description="Comma-separated list of fields to return"),
    sort: Optional[List[str]] = Query(None, description="Sort fields (e.g., 'year:desc,value:asc')"),
):
    """Get fertilizers detailed trade matrix data with advanced filtering and pagination.

    ## Filtering
    - Use comma-separated values for multiple selections (e.g., element_code=102,489)
    - Use _min/_max suffixes for range queries on numeric fields
    - Use _exact suffix for exact string matches

    ## Pagination
    - Use limit and offset parameters
    - Check pagination metadata in response headers

    ## Sorting
    - Use format: field:direction (e.g., 'year:desc')
    - Multiple sorts: 'year:desc,value:asc'
    """

    router_handler = DatasetRouterHandler(
        db=db, 
        model=FertilizersDetailedTradeMatrix, 
        model_name="FertilizersDetailedTradeMatrix",
        table_name="fertilizers_detailed_trade_matrix",
        request=request, 
        response=response, 
        config=config
    )

    reporter_country_code = router_handler.clean_param(reporter_country_code, "multi")
    reporter_countries = router_handler.clean_param(reporter_countries, "like")
    partner_country_code = router_handler.clean_param(partner_country_code, "multi")
    partner_countries = router_handler.clean_param(partner_countries, "like")
    item_code = router_handler.clean_param(item_code, "multi")
    item = router_handler.clean_param(item, "like")
    element_code = router_handler.clean_param(element_code, "multi")
    element = router_handler.clean_param(element, "like")
    flag = router_handler.clean_param(flag, "multi")
    description = router_handler.clean_param(description, "like")
    year_code = router_handler.clean_param(year_code, "like")
    year = router_handler.clean_param(year, "exact")
    year_min = router_handler.clean_param(year_min, "range_min")
    year_max = router_handler.clean_param(year_max, "range_max")
    unit = router_handler.clean_param(unit, "like")
    value = router_handler.clean_param(value, "exact")
    value_min = router_handler.clean_param(value_min, "range_min")
    value_max = router_handler.clean_param(value_max, "range_max")

    param_configs = {
        "limit": limit,
        "offset": offset,
        "reporter_country_code": reporter_country_code,
        "reporter_countries": reporter_countries,
        "partner_country_code": partner_country_code,
        "partner_countries": partner_countries,
        "item_code": item_code,
        "item": item,
        "element_code": element_code,
        "element": element,
        "flag": flag,
        "description": description,
        "year_code": year_code,
        "year": year,
        "year_min": year_min,
        "year_max": year_max,
        "unit": unit,
        "value": value,
        "value_min": value_min,
        "value_max": value_max,
        "fields": fields,
        "sort": sort,
    }
    # Validate field and sort parameter
    requested_fields, sort_columns = router_handler.validate_fields_and_sort_parameters(fields, sort)

    router_handler.validate_filter_parameters(param_configs, db)

    filter_count = router_handler.apply_filters_from_config(param_configs)
    total_count = router_handler.query_builder.get_count(db)

    if sort_columns:
        router_handler.query_builder.add_ordering(sort_columns)
    else:
        router_handler.query_builder.add_ordering(router_handler.get_default_sort())

    # Apply pagination and execute
    results = router_handler.query_builder.paginate(limit, offset).execute(db)

    response_data = router_handler.filter_response_data(results, requested_fields)

    return router_handler.build_response(
        request=request,
        response=response,
        data=response_data,
        total_count=total_count,
        filter_count=filter_count,
        limit=limit,
        offset=offset,
        reporter_country_code=reporter_country_code,
        reporter_countries=reporter_countries,
        partner_country_code=partner_country_code,
        partner_countries=partner_countries,
        item_code=item_code,
        item=item,
        element_code=element_code,
        element=element,
        flag=flag,
        description=description,
        year_code=year_code,
        year=year,
        year_min=year_min,
        year_max=year_max,
        unit=unit,
        value=value,
        value_min=value_min,
        value_max=value_max,
        fields=fields,
        sort=sort,
    )

# templates/partials/router_aggregation_endpoints.jinja2
@router.get("/aggregate", summary="Get aggregated fertilizers detailed trade matrix data")
async def get_fertilizers_detailed_trade_matrix_aggregated(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    # Grouping
    group_by: str = Query(..., description="Comma-separated list of fields to group by"),
    # Aggregations
    aggregations: str = Query(..., description="Comma-separated aggregations (e.g., 'value:sum,value:avg:avg_value')"),
    # Standard
    limit: int = Query(100, ge=0, le=10000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    # Filter parameters
    reporter_country_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by reporter_country_code code (comma-separated for multiple)"),
    reporter_countries: Optional[str] = Query(None, description="Filter by reporter_countries description (partial match)"),
    partner_country_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by partner_country_code code (comma-separated for multiple)"),
    partner_countries: Optional[str] = Query(None, description="Filter by partner_countries description (partial match)"),
    item_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by item_code code (comma-separated for multiple)"),
    item: Optional[str] = Query(None, description="Filter by item description (partial match)"),
    element_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by element_code code (comma-separated for multiple)"),
    element: Optional[str] = Query(None, description="Filter by element description (partial match)"),
    flag: Optional[Union[str, List[str]]] = Query(None, description="Filter by flag code (comma-separated for multiple)"),
    description: Optional[str] = Query(None, description="Filter by description description (partial match)"),
    year_code: Optional[str] = Query(None, description="Filter by year code (partial match)"),
    year: Optional[int] = Query(None, description="Filter by exact year"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    year_max: Optional[int] = Query(None, description="Maximum year"),
    unit: Optional[str] = Query(None, description="Filter by unit (partial match)"),
    value: Optional[Union[float, int]] = Query(None, description="Exact value"),
    value_min: Optional[Union[float, int]] = Query(None, description="Minimum value"),
    value_max: Optional[Union[float, int]] = Query(None, description="Maximum value"),
    # Option parameters  
    fields: Optional[List[str]] = Query(None, description="Comma-separated list of fields to return"),
    sort: Optional[List[str]] = Query(None, description="Sort fields (e.g., 'year:desc,value:asc')"),
):
    """Get aggregated data with grouping and multiple aggregation functions.
    
    ## Examples
    - Sum by year: `group_by=year&aggregations=value:sum`
    - Average by area and year: `group_by=area_code,year&aggregations=value:avg`
    - Multiple aggregations: `aggregations=value:sum:total_value,value:avg:average_value`
    
    ## Aggregation Functions
    - sum, avg, min, max, count, count_distinct
    """
    
    # ------------------------------------------------------------------------
    # Needs same validation: 
    # general values, sort and filter param values, 
    # fk specific validation (checking against actual reference table data)
    # ------------------------------------------------------------------------
    
    
    agg_configs = [parse_aggregation_parameter(a.strip()) for a in aggregations.split(',')]
    
    # Build query
    query_builder = QueryBuilder(select(FertilizersDetailedTradeMatrix))
    filter_count = 0
    joined_tables = set()
    
    # ------------------------
    # Apply same filtering here
    # ------------------------
    
    # Add grouping
    group_columns = [getattr(FertilizersDetailedTradeMatrix, f) for f in group_fields]
    query_builder.add_grouping(group_columns)
    
    # Add aggregations
    for agg_config in agg_configs:
        field = agg_config['field']
        if not hasattr(FertilizersDetailedTradeMatrix, field):
            raise HTTPException(400, f"Invalid aggregation field: {field}")
        
        column = getattr(FertilizersDetailedTradeMatrix, field)
        agg_type = AggregationType(agg_config['function'])
        query_builder.add_aggregation(column, agg_type, agg_config['alias'])
    
    # Apply aggregations
    query_builder.apply_aggregations()
    
    # Get count before pagination
    total_count = query_builder.get_count(db)
    
    # Apply sorting
    if sort:
        # Parse sort fields - can include aggregation aliases
        sort_parts = []
        for sort_field in sort.split(','):
            field, direction = sort_field.strip().split(':')
            
            # Check if it's a group field or aggregation alias
            if field in group_fields:
                column = getattr(FertilizersDetailedTradeMatrix, field)
                sort_parts.append((column, direction))
            else:
                # It might be an aggregation alias - handled by the query
                pass
        
        if sort_parts:
            query_builder.add_ordering(sort_parts)
    
    # Apply pagination and execute
    results = query_builder.paginate(limit, offset).execute(db)
    results = query_builder.parse_results(results)
    
    # Format results
    data = []
    for row in results:
        response_fields = {}
        
        # Add group by fields
        for i, field in enumerate(group_fields):
            response_fields[field] = row[i]
        
        # Add aggregation results
        for j, agg_config in enumerate(agg_configs):
            response_fields[agg_config['alias']] = row[len(group_fields) + j]
        
        data.append(response_fields)
    
    # Build response
    pagination = PaginationBuilder.build_pagination_meta(total_count, limit, offset)

    # Collect all parameters for links
    all_params = {
        'limit': limit,
        'offset': offset,
        'reporter_country_code': reporter_country_code,
        'reporter_countries': reporter_countries,
        'partner_country_code': partner_country_code,
        'partner_countries': partner_countries,
        'item_code': item_code,
        'item': item,
        'element_code': element_code,
        'element': element,
        'flag': flag,
        'description': description,
        'year_code': year_code,
        'year': year,
        'year_min': year_min,
        'year_max': year_max,
        'unit': unit,
        'value': value,
        'value_min': value_min,
        'value_max': value_max,
        'fields': fields,
        'sort': sort,
    }

    links = PaginationBuilder.build_links(
        str(request.url), 
        total_count, 
        limit, 
        offset, 
        all_params
    )

    # Set response headers
    ResponseFormatter.set_pagination_headers(response, total_count, limit, offset, links)

    return ResponseFormatter.format_data_response(data, pagination, links, filter_count)



# ----------------------------------------
# ========== Metadata Endpoints ==========
# ----------------------------------------
@router.get("/reporter_country_codes", summary="Get reporter_country_codes in fertilizers_detailed_trade_matrix")
@cache_result(prefix="fertilizers_detailed_trade_matrix:reporter_country_codes", ttl=604800)
async def get_available_reporter_country_codes(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search reporter_countries by name or code"),
):
    """Get all reporter countries in this trade dataset."""
    query = (
        select(
            ReporterCountryCodes.reporter_country_code,
            ReporterCountryCodes.reporter_countries,
            func.count(FertilizersDetailedTradeMatrix.id).label('record_count')
        )
        .select_from(ReporterCountryCodes)
        .join(FertilizersDetailedTradeMatrix, 
              FertilizersDetailedTradeMatrix.reporter_country_code == ReporterCountryCodes.reporter_country_code)
        .where(ReporterCountryCodes.source_dataset == 'fertilizers_detailed_trade_matrix')
        .group_by(
            ReporterCountryCodes.reporter_country_code,
            ReporterCountryCodes.reporter_countries
        )
    )
    
    if search:
        query = query.where(
            or_(
                ReporterCountryCodes.reporter_countries.ilike(f"%{search}%"),
                ReporterCountryCodes.reporter_country_code.cast(String).like(f"{search}%")
            )
        )
    
    query = query.order_by(ReporterCountryCodes.reporter_country_code)
    results = db.execute(query).all()
    
    return ResponseFormatter.format_metadata_response(
        dataset="fertilizers_detailed_trade_matrix",
        metadata_type="reporter_countries",
        total=len(results),
        items=[
            {
                "reporter_country_code": r.reporter_country_code,
                "reporter_countries": r.reporter_countries,
                "record_count": r.record_count,
            }
            for r in results
        ]
    )

@router.get("/partner_country_codes", summary="Get partner_country_codes in fertilizers_detailed_trade_matrix")
@cache_result(prefix="fertilizers_detailed_trade_matrix:partner_country_codes", ttl=604800)
async def get_available_partner_country_codes(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search partner_countries by name or code"),
    reporter_country_code: Optional[int] = Query(None, description="Filter partners for specific reporter"),
):
    """Get all partner countries in this trade dataset."""

    query = (
        select(
            PartnerCountryCodes.partner_country_code,
            PartnerCountryCodes.partner_countries,
            func.count(FertilizersDetailedTradeMatrix.id).label('record_count')
        )
        .select_from(PartnerCountryCodes)
        .join(FertilizersDetailedTradeMatrix, 
              FertilizersDetailedTradeMatrix.partner_country_code_id == PartnerCountryCodes.id)
        .where(PartnerCountryCodes.source_dataset == 'fertilizers_detailed_trade_matrix')
    )
    
    # Filter by reporter if specified
    if reporter_country_code:
        query = query.join(
            ReporterCountryCodes,
            FertilizersDetailedTradeMatrix.reporter_country_code_id == ReporterCountryCodes.id
        ).where(
            ReporterCountryCodes.reporter_country_code == reporter_country_code
        )
    
    query = query.group_by(
        PartnerCountryCodes.partner_country_code,
        PartnerCountryCodes.partner_countries
    )
    
    if search:
        query = query.where(
            or_(
                PartnerCountryCodes.partner_countries.ilike(f"%{search}%"),
                PartnerCountryCodes.partner_country_code.cast(String).like(f"{search}%")
            )
        )
    
    query = query.order_by(PartnerCountryCodes.partner_country_code)
    results = db.execute(query).all()
    
    response = ResponseFormatter.format_metadata_response(
        dataset="fertilizers_detailed_trade_matrix",
        metadata_type="partner_countries",
        total=len(results),
        items=[
            {
                "partner_country_code": r.partner_country_code,
                "partner_countries": r.partner_countries,
                "record_count": r.record_count,
            }
            for r in results
        ]
    )
    
    if reporter_country_code:
        response["filtered_by_reporter"] = reporter_country_code
    
    return response

@router.get("/item_codes", summary="Get item_codes in fertilizers_detailed_trade_matrix")
@cache_result(prefix="fertilizers_detailed_trade_matrix:item_codes", ttl=604800)
async def get_available_item_codes(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search item by name or code"),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
):
    """Get all items available in this dataset with their codes and metadata."""
    query = (
        select(
            ItemCodes.item_code,
            ItemCodes.item,
            ItemCodes.item_code_cpc,
            ItemCodes.item_code_fbs,
            ItemCodes.item_code_sdg,
            func.count(FertilizersDetailedTradeMatrix.id).label('record_count')
        )
        .select_from(ItemCodes)
        .join(FertilizersDetailedTradeMatrix, FertilizersDetailedTradeMatrix.item_code_id == ItemCodes.id)
        .where(ItemCodes.source_dataset == 'fertilizers_detailed_trade_matrix')
        .group_by(
            ItemCodes.item_code,
            ItemCodes.item,
            ItemCodes.item_code_cpc,
            ItemCodes.item_code_fbs,
            ItemCodes.item_code_sdg
        )
    )
    
    # Apply search filter
    if search:
        query = query.where(
            or_(
                ItemCodes.item.ilike(f"%{search}%"),
                ItemCodes.item_code.cast(String).like(f"{search}%"),
                ItemCodes.item_code_cpc.cast(String).like(f"{search}%"),
                ItemCodes.item_code_fbs.cast(String).like(f"{search}%"),
                ItemCodes.item_code_sdg.cast(String).like(f"{search}%"),
            )
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_count = db.execute(count_query).scalar() or 0
    
    # Apply ordering and pagination
    query = query.order_by(ItemCodes.item_code).limit(limit).offset(offset)
    results = db.execute(query).all()
    
    return ResponseFormatter.format_metadata_response(
        dataset="fertilizers_detailed_trade_matrix",
        metadata_type="items",
        total=total_count,
        items=[
            {
                "item_code": r.item_code,
                "item": r.item,
                "item_code_cpc": r.item_code_cpc,
                "item_code_fbs": r.item_code_fbs,
                "item_code_sdg": r.item_code_sdg,
                "record_count": r.record_count,
            }
            for r in results
        ]
    )

@router.get("/elements", summary="Get elements in fertilizers_detailed_trade_matrix")
@cache_result(prefix="fertilizers_detailed_trade_matrix:elements", ttl=604800)
async def get_available_elements(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search element by name or code"),
):
    """Get all elements (measures/indicators) available in this dataset."""
    query = (
        select(
            Elements.element_code,
            Elements.element,
            func.count(FertilizersDetailedTradeMatrix.id).label('record_count')
        )
        .select_from(Elements)
        .join(FertilizersDetailedTradeMatrix, FertilizersDetailedTradeMatrix.element_code_id == Elements.id)
        .where(Elements.source_dataset == 'fertilizers_detailed_trade_matrix')
        .group_by(
            Elements.element_code,
            Elements.element,
        )
    )
    
    # Apply filters
    if search:
        query = query.where(
            or_(
                Elements.element.ilike(f"%{search}%"),
                Elements.element_code.cast(String).like(f"{search}%")
            )
        )
   
    
    # Execute
    query = query.order_by(Elements.element_code)
    results = db.execute(query).all()
    
    return ResponseFormatter.format_metadata_response(
        dataset="fertilizers_detailed_trade_matrix",
        metadata_type="elements",
        total=len(results),
        items=[
            {
                "element_code": r.element_code,
                "element": r.element,
                "record_count": r.record_count,
            }
            for r in results
        ]
    )

@router.get("/flags", summary="Get flags in fertilizers_detailed_trade_matrix")
@cache_result(prefix="fertilizers_detailed_trade_matrix:flags", ttl=604800)
async def get_available_flags(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search description by name or code"),
    include_distribution: bool = Query(False, description="Include distribution statistics"),
):
    """Get data quality flag information and optionally their distribution in the dataset."""
    # Get all flags used in this dataset
    query = (
        select(
            Flags.id,
            Flags.flag,
            Flags.description,
            func.count(FertilizersDetailedTradeMatrix.id).label('record_count')
        )
        .join(FertilizersDetailedTradeMatrix, Flags.id == FertilizersDetailedTradeMatrix.flag_id)
        .group_by(Flags.flag, Flags.description)
        .order_by(func.count(FertilizersDetailedTradeMatrix.id).desc())
    )

    # Apply search filter
    if search:
        query = query.where(
            or_(
                Flags.description.ilike(f"%{search}%"),
                Flags.flag.cast(String) == search,
            )
        )
    
    flags = db.execute(query).all()
    
    flag_info = []
    for flag in flags:
        info = {
            "flag_id": flag.id,
            "flag": flag.flag,
            "flag_description": flag.flag_description,
        }
        
        if include_distribution:
            # Count records with this flag
            count = db.execute(
                select(func.count())
                .select_from(FertilizersDetailedTradeMatrix)
                .where(FertilizersDetailedTradeMatrix.flag_id == flag.id)
            ).scalar() or 0
            
            info["record_count"] = count
        
        flag_info.append(info)
    
    response = {
        "dataset": "fertilizers_detailed_trade_matrix",
        "total_flags": len(flag_info),
        "flags": flag_info,
    }
    
    if include_distribution:
        # Get total records
        total_records = db.execute(
            select(func.count()).select_from(FertilizersDetailedTradeMatrix)
        ).scalar() or 0
        
        response["total_records"] = total_records
        response["flag_distribution"] = {
            flag["flag"]: {
                "count": flag["record_count"],
                "percentage": round((flag["record_count"] / total_records) * 100, 2) if total_records > 0 else 0
            }
            for flag in flag_info
        }
    
    return response

@router.get("/units", summary="Get units of measurement in fertilizers_detailed_trade_matrix")
@cache_result(prefix="fertilizers_detailed_trade_matrix:units", ttl=604800)
async def get_available_units(db: Session = Depends(get_db)):
    """Get all units of measurement used in this dataset."""
    query = (
        select(
            FertilizersDetailedTradeMatrix.unit,
            func.count(FertilizersDetailedTradeMatrix.id).label('record_count')
        )
        .select_from(FertilizersDetailedTradeMatrix)
        .group_by(FertilizersDetailedTradeMatrix.unit)
        .order_by(FertilizersDetailedTradeMatrix.unit)
    )
    
    results = db.execute(query).all()
    
    return ResponseFormatter.format_metadata_response(
        dataset="fertilizers_detailed_trade_matrix",
        metadata_type="units",
        total=len(results),
        items=[
            {
                "unit": r.unit,
                "record_count": r.record_count,
            }
            for r in results
        ]
    )

@router.get("/years", summary="Get available years in fertilizers_detailed_trade_matrix")
@cache_result(prefix="fertilizers_detailed_trade_matrix:years", ttl=604800)
async def get_available_years(
    db: Session = Depends(get_db),
    include_counts: bool = Query(False, description="Include record counts per year"),
):
    """Get all years with data in this dataset."""
    if include_counts:
        query = (
            select(
                FertilizersDetailedTradeMatrix.year,
                FertilizersDetailedTradeMatrix.year_code,
                func.count(FertilizersDetailedTradeMatrix.id).label('record_count')
            )
            .group_by(FertilizersDetailedTradeMatrix.year, FertilizersDetailedTradeMatrix.year_code)
            .order_by(FertilizersDetailedTradeMatrix.year_code)
        )
        results = db.execute(query).all()
        
        return {
            "dataset": "fertilizers_detailed_trade_matrix",
            "total_years": len(results),
            "year_range": {
                "start": results[0].year if results else None,
                "end": results[-1].year if results else None,
            },
            "years": [
                {
                    "year": r.year,
                    "year_code": r.year_code,
                    "record_count": r.record_count
                }
                for r in results
            ]
        }
    else:
        query = (
            select(FertilizersDetailedTradeMatrix.year)
            .distinct()
            .order_by(FertilizersDetailedTradeMatrix.year)
        )
        results = db.execute(query).all()
        years = [r.year for r in results]
        
        return {
            "dataset": "fertilizers_detailed_trade_matrix",
            "total_years": len(years),
            "year_range": {
                "start": years[0] if years else None,
                "end": years[-1] if years else None,
            },
            "years": years
        }

# -----------------------------------------------
# ========== Dataset Overview Endpoint ==========
# -----------------------------------------------
@router.get("/overview", summary="Get complete overview of fertilizers_detailed_trade_matrix dataset")
@cache_result(prefix="fertilizers_detailed_trade_matrix:overview", ttl=3600)
async def get_dataset_overview(db: Session = Depends(get_db)):
    """Get a complete overview of the dataset including all available dimensions and statistics."""
    overview = {
        "dataset": "fertilizers_detailed_trade_matrix",
        "description": "",
        "last_updated": datetime.utcnow().isoformat(),
        "dimensions": {},
        "statistics": {}
    }
    
    # Total records
    total_records = db.execute(
        select(func.count()).select_from(FertilizersDetailedTradeMatrix)
    ).scalar() or 0
    overview["statistics"]["total_records"] = total_records
    

    reporter_country_code_ids = db.execute(
        select(func.count(func.distinct(FertilizersDetailedTradeMatrix.reporter_country_code_id)))
        .select_from(FertilizersDetailedTradeMatrix)
    ).scalar() or 0

    overview["dimensions"]["reporter_country_codes"] = {
        "count": reporter_country_code_ids,
        "endpoint": f"/fertilizers_detailed_trade_matrix/reporter_country_codes"
    }

    partner_country_code_ids = db.execute(
        select(func.count(func.distinct(FertilizersDetailedTradeMatrix.partner_country_code_id)))
        .select_from(FertilizersDetailedTradeMatrix)
    ).scalar() or 0

    overview["dimensions"]["partner_country_codes"] = {
        "count": partner_country_code_ids,
        "endpoint": f"/fertilizers_detailed_trade_matrix/partner_country_codes"
    }

    item_code_ids = db.execute(
        select(func.count(func.distinct(FertilizersDetailedTradeMatrix.item_code_id)))
        .select_from(FertilizersDetailedTradeMatrix)
    ).scalar() or 0

    overview["dimensions"]["item_codes"] = {
        "count": item_code_ids,
        "endpoint": f"/fertilizers_detailed_trade_matrix/item_codes"
    }

    element_code_ids = db.execute(
        select(func.count(func.distinct(FertilizersDetailedTradeMatrix.element_code_id)))
        .select_from(FertilizersDetailedTradeMatrix)
    ).scalar() or 0

    overview["dimensions"]["elements"] = {
        "count": element_code_ids,
        "endpoint": f"/fertilizers_detailed_trade_matrix/elements"
    }

    flag_ids = db.execute(
        select(func.count(func.distinct(FertilizersDetailedTradeMatrix.flag_id)))
        .select_from(FertilizersDetailedTradeMatrix)
    ).scalar() or 0

    overview["dimensions"]["flags"] = {
        "count": flag_ids,
        "endpoint": f"/fertilizers_detailed_trade_matrix/flags"
    }
    
    # Year range
    year_stats = db.execute(
        select(
            func.min(FertilizersDetailedTradeMatrix.year).label('min_year'),
            func.max(FertilizersDetailedTradeMatrix.year).label('max_year'),
            func.count(func.distinct(FertilizersDetailedTradeMatrix.year)).label('year_count')
        )
        .select_from(FertilizersDetailedTradeMatrix)
    ).first()
    
    overview["dimensions"]["years"] = {
        "range": {
            "start": year_stats.min_year,
            "end": year_stats.max_year
        },
        "count": year_stats.year_count,
        "endpoint": f"/fertilizers_detailed_trade_matrix/years"
    }
    
    # Value statistics
    value_stats = db.execute(
        select(
            func.min(FertilizersDetailedTradeMatrix.value).label('min_value'),
            func.max(FertilizersDetailedTradeMatrix.value).label('max_value'),
            func.avg(FertilizersDetailedTradeMatrix.value).label('avg_value')
        )
        .select_from(FertilizersDetailedTradeMatrix)
        .where(and_(FertilizersDetailedTradeMatrix.value > 0, FertilizersDetailedTradeMatrix.value.is_not(None)))
    ).first()
    
    overview["statistics"]["values"] = {
        "min": float(value_stats.min_value) if value_stats.min_value else None,
        "max": float(value_stats.max_value) if value_stats.max_value else None,
        "average": round(float(value_stats.avg_value), 2) if value_stats.avg_value else None,
    }
    
    # Available endpoints
    overview["endpoints"] = {
        "data": f"/fertilizers_detailed_trade_matrix",
        "aggregate": f"/fertilizers_detailed_trade_matrix/aggregate",
        "summary": f"/fertilizers_detailed_trade_matrix/summary",
        "overview": f"/fertilizers_detailed_trade_matrix/overview",
        "item_codes": f"/fertilizers_detailed_trade_matrix/item_codes",
        "elements": f"/fertilizers_detailed_trade_matrix/elements",
        "flags": f"/fertilizers_detailed_trade_matrix/flags",
    }
    
    return overview

 
@router.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    """Check if the fertilizers_detailed_trade_matrix endpoint is healthy."""
    try:
        # Try to execute a simple query
        result = db.execute(select(func.count()).select_from(FertilizersDetailedTradeMatrix)).scalar()
        return {
            "status": "healthy",
            "dataset": "fertilizers_detailed_trade_matrix",
            "records": result
        }
    except Exception as e:
        raise HTTPException(500, f"Health check failed: {str(e)}")