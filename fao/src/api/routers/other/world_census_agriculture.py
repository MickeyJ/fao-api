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
from fao.src.db.pipelines.world_census_agriculture.world_census_agriculture_model import WorldCensusAgriculture


from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes
from fao.src.db.pipelines.item_codes.item_codes_model import ItemCodes
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

# Import utilities

from fao.src.api.utils.router_handler import RouterHandler
from .world_census_agriculture_config import WorldCensusAgricultureConfig
from fao.src.api.utils.query_helpers import QueryBuilder, AggregationType
from fao.src.api.utils.response_helpers import PaginationBuilder, ResponseFormatter

from fao.src.core.exceptions import (
    invalid_parameter,
    incompatible_parameters,
)

router = APIRouter(
    prefix="/world_census_agriculture",
    responses={404: {"description": "Not found"}},
)


config = WorldCensusAgricultureConfig()

@router.get("/", summary="Get world census agriculture data")
async def get_world_census_agriculture_data(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    # Standard parameters
    limit: int = Query(100, ge=0, le=10000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    # Filter parameters
    area_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by area_code code (comma-separated for multiple)"),
    area: Optional[str] = Query(None, description="Filter by area description (partial match)"),
    item_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by item_code code (comma-separated for multiple)"),
    item: Optional[str] = Query(None, description="Filter by item description (partial match)"),
    element_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by element_code code (comma-separated for multiple)"),
    element: Optional[str] = Query(None, description="Filter by element description (partial match)"),
    flag: Optional[Union[str, List[str]]] = Query(None, description="Filter by flag code (comma-separated for multiple)"),
    description: Optional[str] = Query(None, description="Filter by description description (partial match)"),
    wca_round_code: Optional[str] = Query(None, description="Filter by wca round code (partial match)"),
    wca_round: Optional[int] = Query(None, description="Exact wca round"),
    wca_round_min: Optional[int] = Query(None, description="Minimum wca round"),
    wca_round_max: Optional[int] = Query(None, description="Maximum wca round"),
    census_year_code: Optional[str] = Query(None, description="Filter by census year code (partial match)"),
    census_year: Optional[str] = Query(None, description="Filter by census year (partial match)"),
    unit: Optional[str] = Query(None, description="Filter by unit (partial match)"),
    value: Optional[Union[float, int]] = Query(None, description="Exact value"),
    value_min: Optional[Union[float, int]] = Query(None, description="Minimum value"),
    value_max: Optional[Union[float, int]] = Query(None, description="Maximum value"),
    note: Optional[str] = Query(None, description="Filter by note (partial match)"),
    # Option parameters  
    fields: Optional[List[str]] = Query(None, description="Comma-separated list of fields to return"),
    sort: Optional[List[str]] = Query(None, description="Sort fields (e.g., 'year:desc,value:asc')"),
):
    """Get world census agriculture data with advanced filtering and pagination.

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
        model=WorldCensusAgriculture, 
        model_name="WorldCensusAgriculture",
        table_name="world_census_agriculture",
        request=request, 
        response=response, 
        config=config
    )

    area_code = router_handler.clean_param(area_code, "multi")
    area = router_handler.clean_param(area, "like")
    item_code = router_handler.clean_param(item_code, "multi")
    item = router_handler.clean_param(item, "like")
    element_code = router_handler.clean_param(element_code, "multi")
    element = router_handler.clean_param(element, "like")
    flag = router_handler.clean_param(flag, "multi")
    description = router_handler.clean_param(description, "like")
    wca_round_code = router_handler.clean_param(wca_round_code, "like")
    wca_round = router_handler.clean_param(wca_round, "exact")
    wca_round_min = router_handler.clean_param(wca_round_min, "range_min")
    wca_round_max = router_handler.clean_param(wca_round_max, "range_max")
    census_year_code = router_handler.clean_param(census_year_code, "like")
    census_year = router_handler.clean_param(census_year, "like")
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
        "item_code": item_code,
        "item": item,
        "element_code": element_code,
        "element": element,
        "flag": flag,
        "description": description,
        "wca_round_code": wca_round_code,
        "wca_round": wca_round,
        "wca_round_min": wca_round_min,
        "wca_round_max": wca_round_max,
        "census_year_code": census_year_code,
        "census_year": census_year,
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
        item_code=item_code,
        item=item,
        element_code=element_code,
        element=element,
        flag=flag,
        description=description,
        wca_round_code=wca_round_code,
        wca_round=wca_round,
        wca_round_min=wca_round_min,
        wca_round_max=wca_round_max,
        census_year_code=census_year_code,
        census_year=census_year,
        unit=unit,
        value=value,
        value_min=value_min,
        value_max=value_max,
        note=note,
        fields=fields,
        sort=sort,
    )

# templates/partials/router_aggregation_endpoints.jinja2
@router.get("/aggregate", summary="Get aggregated world census agriculture data")
async def get_world_census_agriculture_aggregated(
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
    item_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by item_code code (comma-separated for multiple)"),
    item: Optional[str] = Query(None, description="Filter by item description (partial match)"),
    element_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by element_code code (comma-separated for multiple)"),
    element: Optional[str] = Query(None, description="Filter by element description (partial match)"),
    flag: Optional[Union[str, List[str]]] = Query(None, description="Filter by flag code (comma-separated for multiple)"),
    description: Optional[str] = Query(None, description="Filter by description description (partial match)"),
    wca_round_code: Optional[str] = Query(None, description="Filter by wca round code (partial match)"),
    wca_round: Optional[int] = Query(None, description="Exact wca round"),
    wca_round_min: Optional[int] = Query(None, description="Minimum wca round"),
    wca_round_max: Optional[int] = Query(None, description="Maximum wca round"),
    census_year_code: Optional[str] = Query(None, description="Filter by census year code (partial match)"),
    census_year: Optional[str] = Query(None, description="Filter by census year (partial match)"),
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
    - sum, avg, min, max, count, count_distinct, stddev, variance, median, string_agg, count_if, sum_if
    """
    
    # ------------------------------------------------------------------------
    # Needs same validation: 
    # general values, sort and filter param values, 
    # fk specific validation (checking against actual reference table data)
    # ------------------------------------------------------------------------
    router_handler = RouterHandler(
        db=db, 
        model=WorldCensusAgriculture, 
        model_name="WorldCensusAgriculture",
        table_name="world_census_agriculture",
        request=request, 
        response=response, 
        config=config
    )

     # Setup aggregation mode
    router_handler.setup_aggregation(group_by, aggregations)

    # Clean parameters
    area_code = router_handler.clean_param(area_code, "multi")
    area = router_handler.clean_param(area, "like")
    item_code = router_handler.clean_param(item_code, "multi")
    item = router_handler.clean_param(item, "like")
    element_code = router_handler.clean_param(element_code, "multi")
    element = router_handler.clean_param(element, "like")
    flag = router_handler.clean_param(flag, "multi")
    description = router_handler.clean_param(description, "like")
    wca_round_code = router_handler.clean_param(wca_round_code, "like")
    wca_round = router_handler.clean_param(wca_round, "exact")
    wca_round_min = router_handler.clean_param(wca_round_min, "range_min")
    wca_round_max = router_handler.clean_param(wca_round_max, "range_max")
    census_year_code = router_handler.clean_param(census_year_code, "like")
    census_year = router_handler.clean_param(census_year, "like")
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
        "item_code": item_code,
        "item": item,
        "element_code": element_code,
        "element": element,
        "flag": flag,
        "description": description,
        "wca_round_code": wca_round_code,
        "wca_round": wca_round,
        "wca_round_min": wca_round_min,
        "wca_round_max": wca_round_max,
        "census_year_code": census_year_code,
        "census_year": census_year,
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
            raise invalid_parameter(
                    params="group_by",
                    value=f"{group_by}",
                    reason=f"Cannot group by '{field}' - field not available. Available fields: {router_handler.query_builder._field_to_column.keys()}",
                )

    router_handler.query_builder.add_grouping(group_columns)
    
    # Add aggregations to query
    for agg_config in router_handler.agg_configs:
        if agg_config['field'] in router_handler.query_builder._field_to_column:
            column = router_handler.query_builder._field_to_column[agg_config['field']]
        else:
            raise invalid_parameter(
                    params="group_by",
                    value=f"{group_by}",
                    reason=f"Cannot aggregate '{agg_config['field']}' - field not available. Available fields: {router_handler.query_builder._field_to_column.keys()}",
                )
        
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
        item_code=item_code,
        item=item,
        element_code=element_code,
        element=element,
        flag=flag,
        description=description,
        wca_round_code=wca_round_code,
        wca_round=wca_round,
        wca_round_min=wca_round_min,
        wca_round_max=wca_round_max,
        census_year_code=census_year_code,
        census_year=census_year,
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
@router.get("/area_codes", summary="Get AreaCodes in world_census_agriculture")
@cache_result(prefix="world_census_agriculture:area_codes", ttl=604800)
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
        .where(AreaCodes.source_dataset == 'world_census_agriculture')
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
                func.count(WorldCensusAgriculture.id).label('record_count')
            )
            .select_from(AreaCodes)
            .join(WorldCensusAgriculture, WorldCensusAgriculture.area_code_id == AreaCodes.id)
            .where(AreaCodes.source_dataset == 'world_census_agriculture')
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
        dataset="world_census_agriculture",
        metadata_type="areas",
        total=total_count,
        items=items
    )

@router.get("/item_codes", summary="Get ItemCodes in world_census_agriculture")
@cache_result(prefix="world_census_agriculture:item_codes", ttl=604800)
async def get_available_item_codes(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search item by name or code"),
    include_distribution: Optional[bool] = Query(False, description="Set True to include distribution statistics"),
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
        )
        .select_from(ItemCodes)
        .where(ItemCodes.source_dataset == 'world_census_agriculture')
        .group_by(
            ItemCodes.item_code,
            ItemCodes.item,
            ItemCodes.item_code_cpc,
            ItemCodes.item_code_fbs,
            ItemCodes.item_code_sdg
        )
    )

    if include_distribution:
        query = (
            select(
                ItemCodes.item_code,
                ItemCodes.item,
                ItemCodes.item_code_cpc,
                ItemCodes.item_code_fbs,
                ItemCodes.item_code_sdg,
                func.count(WorldCensusAgriculture.id).label('record_count')
            )
            .select_from(ItemCodes)
            .join(WorldCensusAgriculture, WorldCensusAgriculture.item_code_id == ItemCodes.id)
            .where(ItemCodes.source_dataset == 'world_census_agriculture')
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

    items = [
        {
            "item_code": r.item_code,
            "item": r.item,
            "item_code_cpc": r.item_code_cpc,
            "item_code_fbs": r.item_code_fbs,
            "item_code_sdg": r.item_code_sdg,
        }
        for r in results
    ]

    if include_distribution:
        items = [
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
    
    return ResponseFormatter.format_metadata_response(
        dataset="world_census_agriculture",
        metadata_type="items",
        total=total_count,
        items=items
    )

@router.get("/elements", summary="Get Elements in world_census_agriculture")
@cache_result(prefix="world_census_agriculture:elements", ttl=604800)
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
        .where(Elements.source_dataset == 'world_census_agriculture')
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
                func.count(WorldCensusAgriculture.id).label('record_count')
            )
            .select_from(Elements)
            .join(WorldCensusAgriculture, Elements.id == WorldCensusAgriculture.element_id)
            .where(Elements.source_dataset == 'world_census_agriculture')
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
        dataset="world_census_agriculture",
        metadata_type="elements",
        total=len(results),
        items=items
    )

@router.get("/flags", summary="Get Flags in world_census_agriculture")
@cache_result(prefix="world_census_agriculture:flags", ttl=604800)
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
            func.count(WorldCensusAgriculture.id).label('record_count')
        )
        .join(WorldCensusAgriculture, Flags.id == WorldCensusAgriculture.flag_id)
        .group_by(Flags.id, Flags.flag, Flags.description)
        .order_by(func.count(WorldCensusAgriculture.id).desc())
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
                .select_from(WorldCensusAgriculture)
                .where(WorldCensusAgriculture.flag_id == flag.id)
            ).scalar() or 0
            
            info["record_count"] = count
        
        flag_info.append(info)
    
    response = {
        "dataset": "world_census_agriculture",
        "total_flags": len(flag_info),
        "flags": flag_info,
    }
    
    if include_distribution:
        # Get total records
        total_records = db.execute(
            select(func.count()).select_from(WorldCensusAgriculture)
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

@router.get("/units", summary="Get units of measurement in world_census_agriculture")
@cache_result(prefix="world_census_agriculture:units", ttl=604800)
async def get_available_units(db: Session = Depends(get_db)):
    """Get all units of measurement used in this dataset."""
    query = (
        select(
            WorldCensusAgriculture.unit,
            func.count(WorldCensusAgriculture.id).label('record_count')
        )
        .select_from(WorldCensusAgriculture)
        .group_by(WorldCensusAgriculture.unit)
        .order_by(WorldCensusAgriculture.unit)
    )
    
    results = db.execute(query).all()
    
    return ResponseFormatter.format_metadata_response(
        dataset="world_census_agriculture",
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

# -----------------------------------------------
# ========== Dataset Overview Endpoint ==========
# -----------------------------------------------
@router.get("/overview", summary="Get complete overview of world_census_agriculture dataset")
@cache_result(prefix="world_census_agriculture:overview", ttl=3600)
async def get_dataset_overview(db: Session = Depends(get_db)):
    """Get a complete overview of the dataset including all available dimensions and statistics."""
    overview = {
        "dataset": "world_census_agriculture",
        "description": "",
        "last_updated": datetime.utcnow().isoformat(),
        "dimensions": {},
        "statistics": {}
    }
    
    # Total records
    total_records = db.execute(
        select(func.count()).select_from(WorldCensusAgriculture)
    ).scalar() or 0
    overview["statistics"]["total_records"] = total_records
    

    area_code_ids = db.execute(
        select(func.count(func.distinct(WorldCensusAgriculture.area_code_id)))
        .select_from(WorldCensusAgriculture)
    ).scalar() or 0

    overview["dimensions"]["area_codes"] = {
        "count": area_code_ids,
        "endpoint": f"/world_census_agriculture/area_codes"
    }

    item_code_ids = db.execute(
        select(func.count(func.distinct(WorldCensusAgriculture.item_code_id)))
        .select_from(WorldCensusAgriculture)
    ).scalar() or 0

    overview["dimensions"]["item_codes"] = {
        "count": item_code_ids,
        "endpoint": f"/world_census_agriculture/item_codes"
    }

    element_code_ids = db.execute(
        select(func.count(func.distinct(WorldCensusAgriculture.element_code_id)))
        .select_from(WorldCensusAgriculture)
    ).scalar() or 0

    overview["dimensions"]["elements"] = {
        "count": element_code_ids,
        "endpoint": f"/world_census_agriculture/elements"
    }

    flag_ids = db.execute(
        select(func.count(func.distinct(WorldCensusAgriculture.flag_id)))
        .select_from(WorldCensusAgriculture)
    ).scalar() or 0

    overview["dimensions"]["flags"] = {
        "count": flag_ids,
        "endpoint": f"/world_census_agriculture/flags"
    }
    
    
    # Value statistics
    value_stats = db.execute(
        select(
            func.min(WorldCensusAgriculture.value).label('min_value'),
            func.max(WorldCensusAgriculture.value).label('max_value'),
            func.avg(WorldCensusAgriculture.value).label('avg_value')
        )
        .select_from(WorldCensusAgriculture)
        .where(and_(WorldCensusAgriculture.value > 0, WorldCensusAgriculture.value.is_not(None)))
    ).first()
    
    overview["statistics"]["values"] = {
        "min": float(value_stats.min_value) if value_stats.min_value else None,
        "max": float(value_stats.max_value) if value_stats.max_value else None,
        "average": round(float(value_stats.avg_value), 2) if value_stats.avg_value else None,
    }
    
    # Available endpoints
    overview["endpoints"] = {
        "data": f"/world_census_agriculture",
        "aggregate": f"/world_census_agriculture/aggregate",
        "summary": f"/world_census_agriculture/summary",
        "overview": f"/world_census_agriculture/overview",
        "area_codes": f"/world_census_agriculture/area_codes",
        "item_codes": f"/world_census_agriculture/item_codes",
        "elements": f"/world_census_agriculture/elements",
        "flags": f"/world_census_agriculture/flags",
    }
    
    return overview

 
@router.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    """Check if the world_census_agriculture endpoint is healthy."""
    try:
        # Try to execute a simple query
        result = db.execute(select(func.count()).select_from(WorldCensusAgriculture)).scalar()
        return {
            "status": "healthy",
            "dataset": "world_census_agriculture",
            "records": result
        }
    except Exception as e:
        raise HTTPException(500, f"Health check failed: {str(e)}")