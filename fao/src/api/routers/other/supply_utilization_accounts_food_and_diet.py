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

from fao.src.api.utils.router_handler import RouterHandler
from .supply_utilization_accounts_food_and_diet_config import SupplyUtilizationAccountsFoodAndDietConfig
from fao.src.api.utils.query_helpers import QueryBuilder, AggregationType
from fao.src.api.utils.response_helpers import PaginationBuilder, ResponseFormatter



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

    router_handler = RouterHandler(
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
    group_by: List[str] = Query(..., description="Comma-separated list of fields to group by"),
    # Aggregations
    aggregations: List[str] = Query(..., description="Comma-separated aggregations (e.g., 'value:sum,value:avg:avg_value')"),
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
    router_handler = RouterHandler(
        db=db, 
        model=SupplyUtilizationAccountsFoodAndDiet, 
        model_name="SupplyUtilizationAccountsFoodAndDiet",
        table_name="supply_utilization_accounts_food_and_diet",
        request=request, 
        response=response, 
        config=config
    )

     # Setup aggregation mode
    router_handler.setup_aggregation(group_by, aggregations)

    # Clean parameters
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
        "sort": sort,
    }

    # Validate fields and sort for aggregation
    if router_handler.is_aggregation:
        # For aggregations, available fields are group_by fields + aggregation aliases
        router_handler.all_data_fields = set(router_handler.get_aggregation_response_fields())
    
    requested_fields, sort_columns = router_handler.validate_fields_and_sort_parameters(fields=[], sort=sort)

    # Validate filter parameters
    router_handler.validate_filter_parameters(param_configs, db)

    # Apply filters
    filter_count = router_handler.apply_filters_from_config(param_configs)
    
    # Add grouping to query
    group_columns = []
    for field in router_handler.group_fields:
        if field in router_handler.query_builder._field_to_column:
            group_columns.append(router_handler.query_builder._field_to_column[field])
        else:
            raise HTTPException(400, f"Cannot group by '{field}' - field not available")

    router_handler.query_builder.add_grouping(group_columns)
    
    # Add aggregations to query
    for agg_config in router_handler.agg_configs:
        if agg_config['field'] in router_handler.query_builder._field_to_column:
            column = router_handler.query_builder._field_to_column[agg_config['field']]
        else:
            raise HTTPException(400, f"Cannot aggregate '{agg_config['field']}' - field not available")
        
        agg_type = AggregationType(agg_config['function'])
        router_handler.query_builder.add_aggregation(column, agg_type, agg_config['alias'], agg_config['round_to'])
    
    # Apply aggregations
    router_handler.query_builder.apply_aggregations()
    
    # Get count
    total_count = router_handler.query_builder.get_count(db)

    # Apply sorting
    if sort_columns:
        router_handler.query_builder.add_ordering(sort_columns)
    else:
        # Default sort for aggregations could be first group field
        if router_handler.group_fields:
            router_handler.query_builder.add_ordering([(router_handler.group_fields[0], "asc")])

    # Execute query
    results = router_handler.query_builder.paginate(limit, offset).execute(db)

    # Format aggregation results
    response_data = router_handler.format_aggregation_results(results)

    print(f"SQL Query: {router_handler.query_builder.query}")

    # Build response
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
        sort=sort,
    )



# ----------------------------------------
# ========== Metadata Endpoints ==========
# ----------------------------------------
@router.get("/area_codes", summary="Get AreaCodes in supply_utilization_accounts_food_and_diet")
@cache_result(prefix="supply_utilization_accounts_food_and_diet:area_codes", ttl=604800)
async def get_available_area_codes(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search area by name or code"),
    include_distribution: Optional[bool] = Query(False, description="Set True to include distribution statistics"),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
):
    """Get all areas (countries/regions) with data in this dataset."""

    query = (
        select(
            AreaCodes.area_code,
            AreaCodes.area,
            AreaCodes.area_code_m49,
        )
        .select_from(AreaCodes)
        .where(AreaCodes.source_dataset == 'supply_utilization_accounts_food_and_diet')
        .group_by(
            AreaCodes.area_code,
            AreaCodes.area,
            AreaCodes.area_code_m49,
        )
    )

    if include_distribution:
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

    items=[
        {
            "area_code": r.area_code,
            "area": r.area,
            "area_code_m49": r.area_code_m49,
        }
        for r in results
    ]

    if include_distribution:
        items=[
            {
                "area_code": r.area_code,
                "area": r.area,
                "area_code_m49": r.area_code_m49,
                "record_count": r.record_count,
            }
            for r in results
        ]
    
    return ResponseFormatter.format_metadata_response(
        dataset="supply_utilization_accounts_food_and_diet",
        metadata_type="areas",
        total=total_count,
        items=items
    )

@router.get("/elements", summary="Get Elements in supply_utilization_accounts_food_and_diet")
@cache_result(prefix="supply_utilization_accounts_food_and_diet:elements", ttl=604800)
async def get_available_elements(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search element by name or code"),
    include_distribution: Optional[bool] = Query(False, description="Set True to include distribution statistics"),
):
    """Get all elements (measures/indicators) available in this dataset."""
    query = (
        select(
            Elements.element_code,
            Elements.element,
        )
        .select_from(Elements)
        .where(Elements.source_dataset == 'supply_utilization_accounts_food_and_diet')
        .group_by(
            Elements.element_code,
            Elements.element,
        )
    )

    if include_distribution:
        query = (
            select(
                Elements.element_code,
                Elements.element,
                func.count(SupplyUtilizationAccountsFoodAndDiet.id).label('record_count')
            )
            .select_from(Elements)
            .join(SupplyUtilizationAccountsFoodAndDiet, Elements.id == SupplyUtilizationAccountsFoodAndDiet.element_id)
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
    items = [
        {
            "element_code": r.element_code,
            "element": r.element,
        }
        for r in results
    ]

    if include_distribution:
        # If distribution is requested, we need to count records for each element
        items = [
            {
                "element_code": r.element_code,
                "element": r.element,
                "record_count": r.record_count,
            }
            for r in results
        ]
        
    return ResponseFormatter.format_metadata_response(
        dataset="supply_utilization_accounts_food_and_diet",
        metadata_type="elements",
        total=len(results),
        items=items
    )

@router.get("/flags", summary="Get Flags in supply_utilization_accounts_food_and_diet")
@cache_result(prefix="supply_utilization_accounts_food_and_diet:flags", ttl=604800)
async def get_available_flags(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search description by name or code"),
    include_distribution: Optional[bool] = Query(False, description="Include distribution statistics"),
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
        .group_by(Flags.id, Flags.flag, Flags.description)
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
            "description": flag.description,
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