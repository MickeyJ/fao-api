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
from fao.src.db.pipelines.individual_quantitative_dietary_data_food_and_diet.individual_quantitative_dietary_data_food_and_diet_model import IndividualQuantitativeDietaryDataFoodAndDiet


from fao.src.db.pipelines.surveys.surveys_model import Surveys
from fao.src.db.pipelines.geographic_levels.geographic_levels_model import GeographicLevels
from fao.src.db.pipelines.population_age_groups.population_age_groups_model import PopulationAgeGroups
from fao.src.db.pipelines.food_groups.food_groups_model import FoodGroups
from fao.src.db.pipelines.indicators.indicators_model import Indicators
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.sexs.sexs_model import Sexs
from fao.src.db.pipelines.flags.flags_model import Flags

# Import utilities
from fao.src.api.utils.dataset_router import DatasetRouterHandler
from .individual_quantitative_dietary_data_food_and_diet_config import IndividualQuantitativeDietaryDataFoodAndDietConfig
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
    is_valid_food_group_code,
    is_valid_geographic_level_code,
    is_valid_indicator_code,
    is_valid_population_age_group_code,
    is_valid_sex_code,
    is_valid_survey_code,
)

from fao.src.core.exceptions import (
    invalid_parameter,
    missing_parameter,
    incompatible_parameters,
    invalid_element_code,
    invalid_flag,
    invalid_food_group_code,
    invalid_geographic_level_code,
    invalid_indicator_code,
    invalid_population_age_group_code,
    invalid_sex_code,
    invalid_survey_code,
)

router = APIRouter(
    prefix="/individual_quantitative_dietary_data_food_and_diet",
    responses={404: {"description": "Not found"}},
)


config = IndividualQuantitativeDietaryDataFoodAndDietConfig()

@router.get("/", summary="Get individual quantitative dietary data food and diet data")
async def get_individual_quantitative_dietary_data_food_and_diet_data(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    # Standard parameters
    limit: int = Query(100, ge=0, le=10000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),

    # Filter parameters
    survey_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by survey_code code (comma-separated for multiple)"),
    survey: Optional[str] = Query(None, description="Filter by survey description (partial match)"),
    geographic_level_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by geographic_level_code code (comma-separated for multiple)"),
    geographic_level: Optional[str] = Query(None, description="Filter by geographic_level description (partial match)"),
    population_age_group_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by population_age_group_code code (comma-separated for multiple)"),
    population_age_group: Optional[str] = Query(None, description="Filter by population_age_group description (partial match)"),
    food_group_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by food_group_code code (comma-separated for multiple)"),
    food_group: Optional[str] = Query(None, description="Filter by food_group description (partial match)"),
    indicator_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by indicator_code code (comma-separated for multiple)"),
    indicator: Optional[str] = Query(None, description="Filter by indicator description (partial match)"),
    element_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by element_code code (comma-separated for multiple)"),
    element: Optional[str] = Query(None, description="Filter by element description (partial match)"),
    sex_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by sex_code code (comma-separated for multiple)"),
    sex: Optional[str] = Query(None, description="Filter by sex description (partial match)"),
    flag: Optional[Union[str, List[str]]] = Query(None, description="Filter by flag code (comma-separated for multiple)"),
    description: Optional[str] = Query(None, description="Filter by description description (partial match)"),
    unit: Optional[str] = Query(None, description="Filter by unit (partial match)"),
    value: Optional[Union[float, int]] = Query(None, description="Exact value"),
    value_min: Optional[Union[float, int]] = Query(None, description="Minimum value"),
    value_max: Optional[Union[float, int]] = Query(None, description="Maximum value"),
    note: Optional[str] = Query(None, description="Filter by note (partial match)"),

    # Option parameters  
    fields: Optional[List[str]] = Query(None, description="Comma-separated list of fields to return"),
    sort: Optional[List[str]] = Query(None, description="Sort fields (e.g., 'year:desc,value:asc')"),
):
    """Get individual quantitative dietary data food and diet data with advanced filtering and pagination.

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
        model=IndividualQuantitativeDietaryDataFoodAndDiet, 
        model_name="IndividualQuantitativeDietaryDataFoodAndDiet",
        table_name="individual_quantitative_dietary_data_food_and_diet",
        request=request, 
        response=response, 
        config=config
    )

    survey_code = router_handler.clean_param(survey_code, "multi")
    survey = router_handler.clean_param(survey, "like")
    geographic_level_code = router_handler.clean_param(geographic_level_code, "multi")
    geographic_level = router_handler.clean_param(geographic_level, "like")
    population_age_group_code = router_handler.clean_param(population_age_group_code, "multi")
    population_age_group = router_handler.clean_param(population_age_group, "like")
    food_group_code = router_handler.clean_param(food_group_code, "multi")
    food_group = router_handler.clean_param(food_group, "like")
    indicator_code = router_handler.clean_param(indicator_code, "multi")
    indicator = router_handler.clean_param(indicator, "like")
    element_code = router_handler.clean_param(element_code, "multi")
    element = router_handler.clean_param(element, "like")
    sex_code = router_handler.clean_param(sex_code, "multi")
    sex = router_handler.clean_param(sex, "like")
    flag = router_handler.clean_param(flag, "multi")
    description = router_handler.clean_param(description, "like")
    unit = router_handler.clean_param(unit, "like")
    value = router_handler.clean_param(value, "exact")
    value_min = router_handler.clean_param(value_min, "range_min")
    value_max = router_handler.clean_param(value_max, "range_max")
    note = router_handler.clean_param(note, "like")

    param_configs = {
        "limit": limit,
        "offset": offset,
        "survey_code": survey_code,
        "survey": survey,
        "geographic_level_code": geographic_level_code,
        "geographic_level": geographic_level,
        "population_age_group_code": population_age_group_code,
        "population_age_group": population_age_group,
        "food_group_code": food_group_code,
        "food_group": food_group,
        "indicator_code": indicator_code,
        "indicator": indicator,
        "element_code": element_code,
        "element": element,
        "sex_code": sex_code,
        "sex": sex,
        "flag": flag,
        "description": description,
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
        survey_code=survey_code,
        survey=survey,
        geographic_level_code=geographic_level_code,
        geographic_level=geographic_level,
        population_age_group_code=population_age_group_code,
        population_age_group=population_age_group,
        food_group_code=food_group_code,
        food_group=food_group,
        indicator_code=indicator_code,
        indicator=indicator,
        element_code=element_code,
        element=element,
        sex_code=sex_code,
        sex=sex,
        flag=flag,
        description=description,
        unit=unit,
        value=value,
        value_min=value_min,
        value_max=value_max,
        note=note,
        fields=fields,
        sort=sort,
    )

# templates/partials/router_aggregation_endpoints.jinja2
@router.get("/aggregate", summary="Get aggregated individual quantitative dietary data food and diet data")
async def get_individual_quantitative_dietary_data_food_and_diet_aggregated(
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
    survey_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by survey_code code (comma-separated for multiple)"),
    survey: Optional[str] = Query(None, description="Filter by survey description (partial match)"),
    geographic_level_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by geographic_level_code code (comma-separated for multiple)"),
    geographic_level: Optional[str] = Query(None, description="Filter by geographic_level description (partial match)"),
    population_age_group_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by population_age_group_code code (comma-separated for multiple)"),
    population_age_group: Optional[str] = Query(None, description="Filter by population_age_group description (partial match)"),
    food_group_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by food_group_code code (comma-separated for multiple)"),
    food_group: Optional[str] = Query(None, description="Filter by food_group description (partial match)"),
    indicator_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by indicator_code code (comma-separated for multiple)"),
    indicator: Optional[str] = Query(None, description="Filter by indicator description (partial match)"),
    element_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by element_code code (comma-separated for multiple)"),
    element: Optional[str] = Query(None, description="Filter by element description (partial match)"),
    sex_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by sex_code code (comma-separated for multiple)"),
    sex: Optional[str] = Query(None, description="Filter by sex description (partial match)"),
    flag: Optional[Union[str, List[str]]] = Query(None, description="Filter by flag code (comma-separated for multiple)"),
    description: Optional[str] = Query(None, description="Filter by description description (partial match)"),
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
    query_builder = QueryBuilder(select(IndividualQuantitativeDietaryDataFoodAndDiet))
    filter_count = 0
    joined_tables = set()
    
    # ------------------------
    # Apply same filtering here
    # ------------------------
    
    # Add grouping
    group_columns = [getattr(IndividualQuantitativeDietaryDataFoodAndDiet, f) for f in group_fields]
    query_builder.add_grouping(group_columns)
    
    # Add aggregations
    for agg_config in agg_configs:
        field = agg_config['field']
        if not hasattr(IndividualQuantitativeDietaryDataFoodAndDiet, field):
            raise HTTPException(400, f"Invalid aggregation field: {field}")
        
        column = getattr(IndividualQuantitativeDietaryDataFoodAndDiet, field)
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
                column = getattr(IndividualQuantitativeDietaryDataFoodAndDiet, field)
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
        'survey_code': survey_code,
        'survey': survey,
        'geographic_level_code': geographic_level_code,
        'geographic_level': geographic_level,
        'population_age_group_code': population_age_group_code,
        'population_age_group': population_age_group,
        'food_group_code': food_group_code,
        'food_group': food_group,
        'indicator_code': indicator_code,
        'indicator': indicator,
        'element_code': element_code,
        'element': element,
        'sex_code': sex_code,
        'sex': sex,
        'flag': flag,
        'description': description,
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
@router.get("/elements", summary="Get elements in individual_quantitative_dietary_data_food_and_diet")
@cache_result(prefix="individual_quantitative_dietary_data_food_and_diet:elements", ttl=604800)
async def get_available_elements(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search element by name or code"),
):
    """Get all elements (measures/indicators) available in this dataset."""
    query = (
        select(
            Elements.element_code,
            Elements.element,
            func.count(IndividualQuantitativeDietaryDataFoodAndDiet.id).label('record_count')
        )
        .select_from(Elements)
        .join(IndividualQuantitativeDietaryDataFoodAndDiet, IndividualQuantitativeDietaryDataFoodAndDiet.element_code_id == Elements.id)
        .where(Elements.source_dataset == 'individual_quantitative_dietary_data_food_and_diet')
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
        dataset="individual_quantitative_dietary_data_food_and_diet",
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

@router.get("/flags", summary="Get flags in individual_quantitative_dietary_data_food_and_diet")
@cache_result(prefix="individual_quantitative_dietary_data_food_and_diet:flags", ttl=604800)
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
            func.count(IndividualQuantitativeDietaryDataFoodAndDiet.id).label('record_count')
        )
        .join(IndividualQuantitativeDietaryDataFoodAndDiet, Flags.id == IndividualQuantitativeDietaryDataFoodAndDiet.flag_id)
        .group_by(Flags.flag, Flags.description)
        .order_by(func.count(IndividualQuantitativeDietaryDataFoodAndDiet.id).desc())
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
                .select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
                .where(IndividualQuantitativeDietaryDataFoodAndDiet.flag_id == flag.id)
            ).scalar() or 0
            
            info["record_count"] = count
        
        flag_info.append(info)
    
    response = {
        "dataset": "individual_quantitative_dietary_data_food_and_diet",
        "total_flags": len(flag_info),
        "flags": flag_info,
    }
    
    if include_distribution:
        # Get total records
        total_records = db.execute(
            select(func.count()).select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
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

@router.get("/units", summary="Get units of measurement in individual_quantitative_dietary_data_food_and_diet")
@cache_result(prefix="individual_quantitative_dietary_data_food_and_diet:units", ttl=604800)
async def get_available_units(db: Session = Depends(get_db)):
    """Get all units of measurement used in this dataset."""
    query = (
        select(
            IndividualQuantitativeDietaryDataFoodAndDiet.unit,
            func.count(IndividualQuantitativeDietaryDataFoodAndDiet.id).label('record_count')
        )
        .select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
        .group_by(IndividualQuantitativeDietaryDataFoodAndDiet.unit)
        .order_by(IndividualQuantitativeDietaryDataFoodAndDiet.unit)
    )
    
    results = db.execute(query).all()
    
    return ResponseFormatter.format_metadata_response(
        dataset="individual_quantitative_dietary_data_food_and_diet",
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
@router.get("/overview", summary="Get complete overview of individual_quantitative_dietary_data_food_and_diet dataset")
@cache_result(prefix="individual_quantitative_dietary_data_food_and_diet:overview", ttl=3600)
async def get_dataset_overview(db: Session = Depends(get_db)):
    """Get a complete overview of the dataset including all available dimensions and statistics."""
    overview = {
        "dataset": "individual_quantitative_dietary_data_food_and_diet",
        "description": "",
        "last_updated": datetime.utcnow().isoformat(),
        "dimensions": {},
        "statistics": {}
    }
    
    # Total records
    total_records = db.execute(
        select(func.count()).select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
    ).scalar() or 0
    overview["statistics"]["total_records"] = total_records
    

    survey_code_ids = db.execute(
        select(func.count(func.distinct(IndividualQuantitativeDietaryDataFoodAndDiet.survey_code_id)))
        .select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["surveys"] = {
        "count": survey_code_ids,
        "endpoint": f"/individual_quantitative_dietary_data_food_and_diet/surveys"
    }

    geographic_level_code_ids = db.execute(
        select(func.count(func.distinct(IndividualQuantitativeDietaryDataFoodAndDiet.geographic_level_code_id)))
        .select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["geographic_levels"] = {
        "count": geographic_level_code_ids,
        "endpoint": f"/individual_quantitative_dietary_data_food_and_diet/geographic_levels"
    }

    population_age_group_code_ids = db.execute(
        select(func.count(func.distinct(IndividualQuantitativeDietaryDataFoodAndDiet.population_age_group_code_id)))
        .select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["population_age_groups"] = {
        "count": population_age_group_code_ids,
        "endpoint": f"/individual_quantitative_dietary_data_food_and_diet/population_age_groups"
    }

    food_group_code_ids = db.execute(
        select(func.count(func.distinct(IndividualQuantitativeDietaryDataFoodAndDiet.food_group_code_id)))
        .select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["food_groups"] = {
        "count": food_group_code_ids,
        "endpoint": f"/individual_quantitative_dietary_data_food_and_diet/food_groups"
    }

    indicator_code_ids = db.execute(
        select(func.count(func.distinct(IndividualQuantitativeDietaryDataFoodAndDiet.indicator_code_id)))
        .select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["indicators"] = {
        "count": indicator_code_ids,
        "endpoint": f"/individual_quantitative_dietary_data_food_and_diet/indicators"
    }

    element_code_ids = db.execute(
        select(func.count(func.distinct(IndividualQuantitativeDietaryDataFoodAndDiet.element_code_id)))
        .select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["elements"] = {
        "count": element_code_ids,
        "endpoint": f"/individual_quantitative_dietary_data_food_and_diet/elements"
    }

    sex_code_ids = db.execute(
        select(func.count(func.distinct(IndividualQuantitativeDietaryDataFoodAndDiet.sex_code_id)))
        .select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["sexs"] = {
        "count": sex_code_ids,
        "endpoint": f"/individual_quantitative_dietary_data_food_and_diet/sexs"
    }

    flag_ids = db.execute(
        select(func.count(func.distinct(IndividualQuantitativeDietaryDataFoodAndDiet.flag_id)))
        .select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
    ).scalar() or 0

    overview["dimensions"]["flags"] = {
        "count": flag_ids,
        "endpoint": f"/individual_quantitative_dietary_data_food_and_diet/flags"
    }
    
    
    # Value statistics
    value_stats = db.execute(
        select(
            func.min(IndividualQuantitativeDietaryDataFoodAndDiet.value).label('min_value'),
            func.max(IndividualQuantitativeDietaryDataFoodAndDiet.value).label('max_value'),
            func.avg(IndividualQuantitativeDietaryDataFoodAndDiet.value).label('avg_value')
        )
        .select_from(IndividualQuantitativeDietaryDataFoodAndDiet)
        .where(and_(IndividualQuantitativeDietaryDataFoodAndDiet.value > 0, IndividualQuantitativeDietaryDataFoodAndDiet.value.is_not(None)))
    ).first()
    
    overview["statistics"]["values"] = {
        "min": float(value_stats.min_value) if value_stats.min_value else None,
        "max": float(value_stats.max_value) if value_stats.max_value else None,
        "average": round(float(value_stats.avg_value), 2) if value_stats.avg_value else None,
    }
    
    # Available endpoints
    overview["endpoints"] = {
        "data": f"/individual_quantitative_dietary_data_food_and_diet",
        "aggregate": f"/individual_quantitative_dietary_data_food_and_diet/aggregate",
        "summary": f"/individual_quantitative_dietary_data_food_and_diet/summary",
        "overview": f"/individual_quantitative_dietary_data_food_and_diet/overview",
        "elements": f"/individual_quantitative_dietary_data_food_and_diet/elements",
        "flags": f"/individual_quantitative_dietary_data_food_and_diet/flags",
    }
    
    return overview

 
@router.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    """Check if the individual_quantitative_dietary_data_food_and_diet endpoint is healthy."""
    try:
        # Try to execute a simple query
        result = db.execute(select(func.count()).select_from(IndividualQuantitativeDietaryDataFoodAndDiet)).scalar()
        return {
            "status": "healthy",
            "dataset": "individual_quantitative_dietary_data_food_and_diet",
            "records": result
        }
    except Exception as e:
        raise HTTPException(500, f"Health check failed: {str(e)}")