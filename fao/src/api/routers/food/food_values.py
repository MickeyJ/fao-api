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
from fao.src.db.pipelines.food_values.food_values_model import FoodValues



# Import utilities
from fao.src.api.utils.dataset_router import DatasetRouterHandler
from .food_values_config import FoodValuesConfig
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
    is_valid_food_value_code,
)

from fao.src.core.exceptions import (
    invalid_parameter,
    missing_parameter,
    incompatible_parameters,
    invalid_food_value_code,
)

router = APIRouter(
    prefix="/food_values",
    responses={404: {"description": "Not found"}},
)


config = FoodValuesConfig()

@router.get("/", summary="Get food values data")
async def get_food_values_data(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    # Standard parameters
    limit: int = Query(100, ge=0, le=10000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),

    # Filter parameters
    food_value_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by food value code (comma-separated for multiple)"),
    food_value: Optional[str] = Query(None, description="Filter by food value (partial match)"),
    source_dataset: Optional[str] = Query(None, description="Filter by source dataset (partial match)"),

    # Option parameters  
    fields: Optional[List[str]] = Query(None, description="Comma-separated list of fields to return"),
    sort: Optional[List[str]] = Query(None, description="Sort fields (e.g., 'year:desc,value:asc')"),
):
    """Get food values data with advanced filtering and pagination.

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
        model=FoodValues, 
        model_name="FoodValues",
        table_name="food_values",
        request=request, 
        response=response, 
        config=config
    )

    food_value_code = router_handler.clean_param(food_value_code, "multi")
    food_value = router_handler.clean_param(food_value, "like")
    source_dataset = router_handler.clean_param(source_dataset, "like")

    param_configs = {
        "limit": limit,
        "offset": offset,
        "food_value_code": food_value_code,
        "food_value": food_value,
        "source_dataset": source_dataset,
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
        food_value_code=food_value_code,
        food_value=food_value,
        source_dataset=source_dataset,
        fields=fields,
        sort=sort,
    )

@router.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    """Check if the food_values endpoint is healthy."""
    try:
        # Try to execute a simple query
        result = db.execute(select(func.count()).select_from(FoodValues)).scalar()
        return {
            "status": "healthy",
            "dataset": "food_values",
            "records": result
        }
    except Exception as e:
        raise HTTPException(500, f"Health check failed: {str(e)}")