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
from fao.src.db.pipelines.factors.factors_model import Factors



# Import utilities

from fao.src.api.utils.router_handler import RouterHandler
from .factors_config import FactorsConfig
from fao.src.api.utils.query_helpers import QueryBuilder, AggregationType
from fao.src.api.utils.response_helpers import PaginationBuilder, ResponseFormatter

from fao.src.core.exceptions import (
    invalid_parameter,
    incompatible_parameters,
)

router = APIRouter(
    prefix="/factors",
    responses={404: {"description": "Not found"}},
)


config = FactorsConfig()

@router.get("/", summary="Get factors data")
async def get_factors_data(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    # Standard parameters
    limit: int = Query(100, ge=0, le=10000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    # Filter parameters
    factor_code: Optional[Union[str, List[str]]] = Query(None, description="Filter by factor code (comma-separated for multiple)"),
    factor: Optional[str] = Query(None, description="Filter by factor (partial match)"),
    source_dataset: Optional[str] = Query(None, description="Filter by source dataset (partial match)"),
    # Option parameters  
    fields: Optional[List[str]] = Query(None, description="Comma-separated list of fields to return"),
    sort: Optional[List[str]] = Query(None, description="Sort fields (e.g., 'year:desc,value:asc')"),
):
    """Get factors data with advanced filtering and pagination.

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
        model=Factors, 
        model_name="Factors",
        table_name="factors",
        request=request, 
        response=response, 
        config=config
    )

    factor_code = router_handler.clean_param(factor_code, "multi")
    factor = router_handler.clean_param(factor, "like")
    source_dataset = router_handler.clean_param(source_dataset, "like")

    param_configs = {
        "limit": limit,
        "offset": offset,
        "factor_code": factor_code,
        "factor": factor,
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
        factor_code=factor_code,
        factor=factor,
        source_dataset=source_dataset,
        fields=fields,
        sort=sort,
    )

@router.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    """Check if the factors endpoint is healthy."""
    try:
        # Try to execute a simple query
        result = db.execute(select(func.count()).select_from(Factors)).scalar()
        return {
            "status": "healthy",
            "dataset": "factors",
            "records": result
        }
    except Exception as e:
        raise HTTPException(500, f"Health check failed: {str(e)}")