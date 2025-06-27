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
from fao.src.db.pipelines.food_groups.food_groups_model import FoodGroups



# Import utilities

from fao.src.api.utils.router_handler import RouterHandler
from .food_groups_config import FoodGroupsConfig
from fao.src.api.utils.query_helpers import QueryBuilder, AggregationType
from fao.src.api.utils.response_helpers import PaginationBuilder, ResponseFormatter



router = APIRouter(
    prefix="/food_groups",
    responses={404: {"description": "Not found"}},
)


config = FoodGroupsConfig()

@router.get("/", summary="Get food groups data")
async def get_food_groups_data(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    # Standard parameters
    limit: int = Query(100, ge=0, le=10000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    # Filter parameters
    food_group_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by food group code (comma-separated for multiple)"),
    food_group: Optional[str] = Query(None, description="Filter by food group (partial match)"),
    source_dataset: Optional[str] = Query(None, description="Filter by source dataset (partial match)"),
    # Option parameters  
    fields: Optional[List[str]] = Query(None, description="Comma-separated list of fields to return"),
    sort: Optional[List[str]] = Query(None, description="Sort fields (e.g., 'year:desc,value:asc')"),
):
    """Get food groups data with advanced filtering and pagination.

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
        model=FoodGroups, 
        model_name="FoodGroups",
        table_name="food_groups",
        request=request, 
        response=response, 
        config=config
    )

    food_group_code = router_handler.clean_param(food_group_code, "multi")
    food_group = router_handler.clean_param(food_group, "like")
    source_dataset = router_handler.clean_param(source_dataset, "like")

    param_configs = {
        "limit": limit,
        "offset": offset,
        "food_group_code": food_group_code,
        "food_group": food_group,
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
        food_group_code=food_group_code,
        food_group=food_group,
        source_dataset=source_dataset,
        fields=fields,
        sort=sort,
    )

@router.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    """Check if the food_groups endpoint is healthy."""
    try:
        # Try to execute a simple query
        result = db.execute(select(func.count()).select_from(FoodGroups)).scalar()
        return {
            "status": "healthy",
            "dataset": "food_groups",
            "records": result
        }
    except Exception as e:
        raise HTTPException(500, f"Health check failed: {str(e)}")