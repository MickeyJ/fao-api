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
from fao.src.db.pipelines.supply_utilization_accounts_food_and_diet.supply_utilization_accounts_food_and_diet_model import SupplyUtilizationAccountsFoodAndDiet


from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes
from fao.src.db.pipelines.food_groups.food_groups_model import FoodGroups
from fao.src.db.pipelines.indicators.indicators_model import Indicators
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

# Import utilities
from fao.src.api.utils.dataset_router import DatasetRouterHandler
from .supply_utilization_accounts_food_and_diet_config import SupplyUtilizationAccountsFoodAndDietConfig
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
    is_valid_area_code,
    is_valid_element_code,
    is_valid_flag,
    is_valid_food_group_code,
    is_valid_indicator_code,
)

from fao.src.core.exceptions import (
    invalid_parameter,
    missing_parameter,
    incompatible_parameters,
    invalid_area_code,
    invalid_element_code,
    invalid_flag,
    invalid_food_group_code,
    invalid_indicator_code,
)

router = APIRouter(
    prefix="/supply_utilization_accounts_food_and_diet",
    responses={404: {"description": "Not found"}},
)


config = SupplyUtilizationAccountsFoodAndDietConfig()

@router.get("/", summary="Get supply utilization accounts food and diet data")
async def get_supply_utilization_accounts_food_and_diet_data(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    # Standard parameters
    limit: int = Query(100, ge=0, le=10000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),

    # Filter parameters
    area_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by area_code code (comma-separated for multiple)"),
    area: Optional[str] = Query(None, description="Filter by area description (partial match)"),
    food_group_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by food_group_code code (comma-separated for multiple)"),
    food_group: Optional[str] = Query(None, description="Filter by food_group description (partial match)"),
    indicator_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by indicator_code code (comma-separated for multiple)"),
    indicator: Optional[str] = Query(None, description="Filter by indicator description (partial match)"),
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
    note: Optional[str] = Query(None, description="Filter by note (partial match)"),

    # Option parameters  
    fields: Optional[List[str]] = Query(None, description="Comma-separated list of fields to return"),
    sort: Optional[List[str]] = Query(None, description="Sort fields (e.g., 'year:desc,value:asc')"),
):
    """Get supply utilization accounts food and diet data with advanced filtering and pagination.

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
        model=SupplyUtilizationAccountsFoodAndDiet, 
        model_name="SupplyUtilizationAccountsFoodAndDiet",
        table_name="supply_utilization_accounts_food_and_diet",
        request=request, 
        response=response, 
        config=config
    )

    area_code = router_handler.clean_param(area_code, "multi")
    area = router_handler.clean_param(area, "like")
    food_group_code = router_handler.clean_param(food_group_code, "multi")
    food_group = router_handler.clean_param(food_group, "like")
    indicator_code = router_handler.clean_param(indicator_code, "multi")
    indicator = router_handler.clean_param(indicator, "like")
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
    note = router_handler.clean_param(note, "like")

    param_configs = {
        "limit": limit,
        "offset": offset,
        "area_code": area_code,
        "area": area,
        "food_group_code": food_group_code,
        "food_group": food_group,
        "indicator_code": indicator_code,
        "indicator": indicator,
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
        "note": note,
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
        area_code=area_code,
        area=area,
        food_group_code=food_group_code,
        food_group=food_group,
        indicator_code=indicator_code,
        indicator=indicator,
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
        note=note,
        fields=fields,
        sort=sort,
    )

# templates/partials/router_aggregation_endpoints.jinja2
@router.get("/aggregate", summary="Get aggregated supply utilization accounts food and diet data")
async def get_supply_utilization_accounts_food_and_diet_aggregated(
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
    area_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by area_code code (comma-separated for multiple)"),
    area: Optional[str] = Query(None, description="Filter by area description (partial match)"),
    food_group_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by food_group_code code (comma-separated for multiple)"),
    food_group: Optional[str] = Query(None, description="Filter by food_group description (partial match)"),
    indicator_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by indicator_code code (comma-separated for multiple)"),
    indicator: Optional[str] = Query(None, description="Filter by indicator description (partial match)"),
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
    note: Optional[str] = Query(None, description="Filter by note (partial match)"),
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
    query_builder = QueryBuilder(select(SupplyUtilizationAccountsFoodAndDiet))
    filter_count = 0
    joined_tables = set()
    
    # ------------------------
    # Apply same filtering here
    # ------------------------
    
    # Add grouping
    group_columns = [getattr(SupplyUtilizationAccountsFoodAndDiet, f) for f in group_fields]
    query_builder.add_grouping(group_columns)
    
    # Add aggregations
    for agg_config in agg_configs:
        field = agg_config['field']
        if not hasattr(SupplyUtilizationAccountsFoodAndDiet, field):
            raise HTTPException(400, f"Invalid aggregation field: {field}")
        
        column = getattr(SupplyUtilizationAccountsFoodAndDiet, field)
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
                column = getattr(SupplyUtilizationAccountsFoodAndDiet, field)
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
        'area_code': area_code,
        'area': area,
        'food_group_code': food_group_code,
        'food_group': food_group,
        'indicator_code': indicator_code,
        'indicator': indicator,
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
        'note': note,
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
@router.get("/area_codes", summary="Get area_codes in supply_utilization_accounts_food_and_diet")
@cache_result(prefix="supply_utilization_accounts_food_and_diet:area_codes", ttl=604800)
async def get_available_area_codes(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search area by name or code"),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
):
    """Get all areas (countries/regions) with data in this dataset."""
    query = (
        select(
            AreaCodes.area_code,
            AreaCodes.area,
            AreaCodes.area_code_m49,
            func.count(SupplyUtilizationAccountsFoodAndDiet.id).label('record_count')
        )
        .select_from(AreaCodes)
        .join(SupplyUtilizationAccountsFoodAndDiet, SupplyUtilizationAccountsFoodAndDiet.area_code_id == AreaCodes.id)
        .where(AreaCodes.source_dataset == 'supply_utilization_accounts_food_and_diet')
        .group_by(
            AreaCodes.area_code,
            AreaCodes.area,
            AreaCodes.area_code_m49,
        )
    )
    
    # Apply filters
    if search:
        query = query.where(
            or_(
                AreaCodes.area.ilike(f"%{search}%"),
                AreaCodes.area_code.cast(String).like(f"{search}%"),
                AreaCodes.area_code_m49.cast(String).like(f"{search}%"),
            )
        )
    
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_count = db.execute(count_query).scalar() or 0
    
    # Apply ordering and pagination
    query = query.order_by(AreaCodes.area_code).limit(limit).offset(offset)
    results = db.execute(query).all()
    
    return ResponseFormatter.format_metadata_response(
        dataset="supply_utilization_accounts_food_and_diet",
        metadata_type="areas",
        total=total_count,
        items=[
            {
                "area_code": r.area_code,
                "area": r.area,
                "area_code_m49": r.area_code_m49,
                "record_count": r.record_count,
            }
            for r in results
        ]
    )

@router.get("/elements", summary="Get elements in supply_utilization_accounts_food_and_diet")
@cache_result(prefix="supply_utilization_accounts_food_and_diet:elements", ttl=604800)
async def get_available_elements(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search element by name or code"),
):
    """Get all elements (measures/indicators) available in this dataset."""
    query = (
        select(
            Elements.element_code,
            Elements.element,
            func.count(SupplyUtilizationAccountsFoodAndDiet.id).label('record_count')
        )
        .select_from(Elements)
        .join(SupplyUtilizationAccountsFoodAndDiet, SupplyUtilizationAccountsFoodAndDiet.element_code_id == Elements.id)
        .where(Elements.source_dataset == 'supply_utilization_accounts_food_and_diet')
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
        dataset="supply_utilization_accounts_food_and_diet",
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

@router.get("/flags", summary="Get flags in supply_utilization_accounts_food_and_diet")
@cache_result(prefix="supply_utilization_accounts_food_and_diet:flags", ttl=604800)
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
            func.count(SupplyUtilizationAccountsFoodAndDiet.id).label('record_count')
        )
        .join(SupplyUtilizationAccountsFoodAndDiet, Flags.id == SupplyUtilizationAccountsFoodAndDiet.flag_id)
        .group_by(Flags.flag, Flags.description)
        .order_by(func.count(SupplyUtilizationAccountsFoodAndDiet.id).desc())
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
                .select_from(SupplyUtilizationAccountsFoodAndDiet)
                .where(SupplyUtilizationAccountsFoodAndDiet.flag_id == flag.id)
            ).scalar() or 0
            
            info["record_count"] = count
        
        flag_info.append(info)
    
    response = {
        "dataset": "supply_utilization_accounts_food_and_diet",
        "total_flags": len(flag_info),
        "flags": flag_info,
    }
    
    if include_distribution:
        # Get total records
        total_records = db.execute(
            select(func.count()).select_from(SupplyUtilizationAccountsFoodAndDiet)
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

@router.get("/units", summary="Get units of measurement in supply_utilization_accounts_food_and_diet")
@cache_result(prefix="supply_utilization_accounts_food_and_diet:units", ttl=604800)
async def get_available_units(db: Session = Depends(get_db)):
    """Get all units of measurement used in this dataset."""
    query = (
        select(
            SupplyUtilizationAccountsFoodAndDiet.unit,
            func.count(SupplyUtilizationAccountsFoodAndDiet.id).label('record_count')
        )
        .select_from(SupplyUtilizationAccountsFoodAndDiet)
        .group_by(SupplyUtilizationAccountsFoodAndDiet.unit)
        .order_by(SupplyUtilizationAccountsFoodAndDiet.unit)
    )
    
    results = db.execute(query).all()
    
    return ResponseFormatter.format_metadata_response(
        dataset="supply_utilization_accounts_food_and_diet",
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

@router.get("/years", summary="Get available years in supply_utilization_accounts_food_and_diet")
@cache_result(prefix="supply_utilization_accounts_food_and_diet:years", ttl=604800)
async def get_available_years(
    db: Session = Depends(get_db),
    include_counts: bool = Query(False, description="Include record counts per year"),
):
    """Get all years with data in this dataset."""
    if include_counts:
        query = (
            select(
                SupplyUtilizationAccountsFoodAndDiet.year,
                SupplyUtilizationAccountsFoodAndDiet.year_code,
                func.count(SupplyUtilizationAccountsFoodAndDiet.id).label('record_count')
            )
            .group_by(SupplyUtilizationAccountsFoodAndDiet.year, SupplyUtilizationAccountsFoodAndDiet.year_code)
            .order_by(SupplyUtilizationAccountsFoodAndDiet.year_code)
        )
        results = db.execute(query).all()
        
        return {
            "dataset": "supply_utilization_accounts_food_and_diet",
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
            select(SupplyUtilizationAccountsFoodAndDiet.year)
            .distinct()
            .order_by(SupplyUtilizationAccountsFoodAndDiet.year)
        )
        results = db.execute(query).all()
        years = [r.year for r in results]
        
        return {
            "dataset": "supply_utilization_accounts_food_and_diet",
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
@router.get("/overview", summary="Get complete overview of supply_utilization_accounts_food_and_diet dataset")
@cache_result(prefix="supply_utilization_accounts_food_and_diet:overview", ttl=3600)
async def get_dataset_overview(db: Session = Depends(get_db)):
    """Get a complete overview of the dataset including all available dimensions and statistics."""
    overview = {
        "dataset": "supply_utilization_accounts_food_and_diet",
        "description": "",
        "last_updated": datetime.utcnow().isoformat(),
        "dimensions": {},
        "statistics": {}
    }
    
    # Total records
    total_records = db.execute(
        select(func.count()).select_from(SupplyUtilizationAccountsFoodAndDiet)
    ).scalar() or 0
    overview["statistics"]["total_records"] = total_records
    

    area_code_ids = db.execute(
        select(func.count(func.distinct(SupplyUtilizationAccountsFoodAndDiet.area_code_id)))
        .select_from(SupplyUtilizationAccountsFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["area_codes"] = {
        "count": area_code_ids,
        "endpoint": f"/supply_utilization_accounts_food_and_diet/area_codes"
    }

    food_group_code_ids = db.execute(
        select(func.count(func.distinct(SupplyUtilizationAccountsFoodAndDiet.food_group_code_id)))
        .select_from(SupplyUtilizationAccountsFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["food_groups"] = {
        "count": food_group_code_ids,
        "endpoint": f"/supply_utilization_accounts_food_and_diet/food_groups"
    }

    indicator_code_ids = db.execute(
        select(func.count(func.distinct(SupplyUtilizationAccountsFoodAndDiet.indicator_code_id)))
        .select_from(SupplyUtilizationAccountsFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["indicators"] = {
        "count": indicator_code_ids,
        "endpoint": f"/supply_utilization_accounts_food_and_diet/indicators"
    }

    element_code_ids = db.execute(
        select(func.count(func.distinct(SupplyUtilizationAccountsFoodAndDiet.element_code_id)))
        .select_from(SupplyUtilizationAccountsFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["elements"] = {
        "count": element_code_ids,
        "endpoint": f"/supply_utilization_accounts_food_and_diet/elements"
    }

    flag_ids = db.execute(
        select(func.count(func.distinct(SupplyUtilizationAccountsFoodAndDiet.flag_id)))
        .select_from(SupplyUtilizationAccountsFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["flags"] = {
        "count": flag_ids,
        "endpoint": f"/supply_utilization_accounts_food_and_diet/flags"
    }
    
    # Year range
    year_stats = db.execute(
        select(
            func.min(SupplyUtilizationAccountsFoodAndDiet.year).label('min_year'),
            func.max(SupplyUtilizationAccountsFoodAndDiet.year).label('max_year'),
            func.count(func.distinct(SupplyUtilizationAccountsFoodAndDiet.year)).label('year_count')
        )
        .select_from(SupplyUtilizationAccountsFoodAndDiet)
    ).first()
    
    overview["dimensions"]["years"] = {
        "range": {
            "start": year_stats.min_year,
            "end": year_stats.max_year
        },
        "count": year_stats.year_count,
        "endpoint": f"/supply_utilization_accounts_food_and_diet/years"
    }
    
    # Value statistics
    value_stats = db.execute(
        select(
            func.min(SupplyUtilizationAccountsFoodAndDiet.value).label('min_value'),
            func.max(SupplyUtilizationAccountsFoodAndDiet.value).label('max_value'),
            func.avg(SupplyUtilizationAccountsFoodAndDiet.value).label('avg_value')
        )
        .select_from(SupplyUtilizationAccountsFoodAndDiet)
        .where(and_(SupplyUtilizationAccountsFoodAndDiet.value > 0, SupplyUtilizationAccountsFoodAndDiet.value.is_not(None)))
    ).first()
    
    overview["statistics"]["values"] = {
        "min": float(value_stats.min_value) if value_stats.min_value else None,
        "max": float(value_stats.max_value) if value_stats.max_value else None,
        "average": round(float(value_stats.avg_value), 2) if value_stats.avg_value else None,
    }
    
    # Available endpoints
    overview["endpoints"] = {
        "data": f"/supply_utilization_accounts_food_and_diet",
        "aggregate": f"/supply_utilization_accounts_food_and_diet/aggregate",
        "summary": f"/supply_utilization_accounts_food_and_diet/summary",
        "overview": f"/supply_utilization_accounts_food_and_diet/overview",
        "area_codes": f"/supply_utilization_accounts_food_and_diet/area_codes",
        "elements": f"/supply_utilization_accounts_food_and_diet/elements",
        "flags": f"/supply_utilization_accounts_food_and_diet/flags",
    }
    
    return overview

 
@router.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    """Check if the supply_utilization_accounts_food_and_diet endpoint is healthy."""
    try:
        # Try to execute a simple query
        result = db.execute(select(func.count()).select_from(SupplyUtilizationAccountsFoodAndDiet)).scalar()
        return {
            "status": "healthy",
            "dataset": "supply_utilization_accounts_food_and_diet",
            "records": result
        }
    except Exception as e:
        raise HTTPException(500, f"Health check failed: {str(e)}")