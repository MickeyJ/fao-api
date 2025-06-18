from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, text, String, Integer, Float, SmallInteger
from typing import Optional, Union, Dict, List
from fao.src.core.cache import cache_result
from fao.src.core import settings
from fao.src.db.database import get_db
from fao.src.db.pipelines.household_consumption_and_expenditure_surveys_food_and_diet.household_consumption_and_expenditure_surveys_food_and_diet_model import HouseholdConsumptionAndExpenditureSurveysFoodAndDiet
import math
from datetime import datetime
# Import core/reference tables for joins
from fao.src.db.pipelines.surveys.surveys_model import Surveys
from fao.src.db.pipelines.geographic_levels.geographic_levels_model import GeographicLevels
from fao.src.db.pipelines.food_groups.food_groups_model import FoodGroups
from fao.src.db.pipelines.indicators.indicators_model import Indicators
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

router = APIRouter(
    prefix="/household_consumption_and_expenditure_surveys_food_and_diet",
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
@cache_result(prefix="household_consumption_and_expenditure_surveys_food_and_diet", ttl=86400, exclude_params=["response", "db"])
def get_household_consumption_and_expenditure_surveys_food_and_diet(
    response: Response,
    limit: int = Query(100, le=1000, ge=1, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    survey_code: Optional[str] = Query(None, description="Filter by surveys code"),
    survey: Optional[str] = Query(None, description="Filter by surveys description"),
    geographic_level_code: Optional[str] = Query(None, description="Filter by geographic_levels code"),
    geographic_level: Optional[str] = Query(None, description="Filter by geographic_levels description"),
    food_group_code: Optional[str] = Query(None, description="Filter by food_groups code"),
    food_group: Optional[str] = Query(None, description="Filter by food_groups description"),
    indicator_code: Optional[str] = Query(None, description="Filter by indicators code"),
    indicator: Optional[str] = Query(None, description="Filter by indicators description"),
    element_code: Optional[str] = Query(None, description="Filter by elements code"),
    element: Optional[str] = Query(None, description="Filter by elements description"),
    flag: Optional[str] = Query(None, description="Filter by flags code"),
    description: Optional[str] = Query(None, description="Filter by flags description"),
    # Dynamic column filters based on model
    unit: Optional[str] = Query(None, description="Filter by unit (partial match)"),
    unit_exact: Optional[str] = Query(None, description="Filter by exact unit"),
    value: Optional[Union[float, int]] = Query(None, description="Exact value"),
    value_min: Optional[Union[float, int]] = Query(None, description="Minimum value"),
    value_max: Optional[Union[float, int]] = Query(None, description="Maximum value"),
    note: Optional[str] = Query(None, description="Filter by note (partial match)"),
    note_exact: Optional[str] = Query(None, description="Filter by exact note"),
    include_all_reference_columns: bool = Query(False, description="Include all columns from reference tables"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to return"),
    sort: Optional[str] = Query(None, description="Sort fields (use - prefix for descending, e.g., 'year,-value')"),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get household consumption and expenditure surveys food and diet data with filters and pagination.
    
    ## Pagination
    - Use `limit` and `offset` for page-based navigation
    - Response includes pagination metadata and total count
    - Link headers provided for easy navigation
    
    ## Filtering
    - survey_code: Filter by surveys code
    - survey: Filter by surveys description (partial match)
    - geographic_level_code: Filter by geographic_levels code
    - geographic_level: Filter by geographic_levels description (partial match)
    - food_group_code: Filter by food_groups code
    - food_group: Filter by food_groups description (partial match)
    - indicator_code: Filter by indicators code
    - indicator: Filter by indicators description (partial match)
    - element_code: Filter by elements code
    - element: Filter by elements description (partial match)
    - flag: Filter by flags code
    - description: Filter by flags description (partial match)
    
    Dataset-specific filters:
    - unit: Partial match (case-insensitive)
    - unit_exact: Exact match
    - value: Exact value
    - value_min/value_max: Value range
    - note: Partial match (case-insensitive)
    - note_exact: Exact match
    
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
    for col in HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.__table__.columns:
        if col.name not in ['created_at', 'updated_at']:
            column_map[col.name] = col
    
    # Reference table columns
    if include_all_reference_columns:
        # Add all reference columns
        for col in Surveys.__table__.columns:
            if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                col_alias = "surveys_" + col.name
                column_map[col_alias] = col.label(col_alias)
    else:
        # Just key columns
        col_alias = "surveys_survey_code"
        column_map[col_alias] = Surveys.survey_code.label(col_alias)
        col_alias = "surveys_survey"
        column_map[col_alias] = Surveys.survey.label(col_alias)
    if include_all_reference_columns:
        # Add all reference columns
        for col in GeographicLevels.__table__.columns:
            if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                col_alias = "geographic_levels_" + col.name
                column_map[col_alias] = col.label(col_alias)
    else:
        # Just key columns
        col_alias = "geographic_levels_geographic_level_code"
        column_map[col_alias] = GeographicLevels.geographic_level_code.label(col_alias)
        col_alias = "geographic_levels_geographic_level"
        column_map[col_alias] = GeographicLevels.geographic_level.label(col_alias)
    if include_all_reference_columns:
        # Add all reference columns
        for col in FoodGroups.__table__.columns:
            if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                col_alias = "food_groups_" + col.name
                column_map[col_alias] = col.label(col_alias)
    else:
        # Just key columns
        col_alias = "food_groups_food_group_code"
        column_map[col_alias] = FoodGroups.food_group_code.label(col_alias)
        col_alias = "food_groups_food_group"
        column_map[col_alias] = FoodGroups.food_group.label(col_alias)
    if include_all_reference_columns:
        # Add all reference columns
        for col in Indicators.__table__.columns:
            if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                col_alias = "indicators_" + col.name
                column_map[col_alias] = col.label(col_alias)
    else:
        # Just key columns
        col_alias = "indicators_indicator_code"
        column_map[col_alias] = Indicators.indicator_code.label(col_alias)
        col_alias = "indicators_indicator"
        column_map[col_alias] = Indicators.indicator.label(col_alias)
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
            elif field_name == 'id' and hasattr(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet, 'id'):
                columns.append(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.id)
    else:
        # No specific fields requested, use all available columns in default order
        for col in HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.__table__.columns:
            if col.name not in ['created_at', 'updated_at']:
                columns.append(col)
        
        # Add reference columns in default order
        if include_all_reference_columns:
            for col in Surveys.__table__.columns:
                if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                    columns.append(col.label("surveys_" + col.name))
        else:
            columns.append(Surveys.survey_code.label("surveys_survey_code"))
            columns.append(Surveys.survey.label("surveys_survey"))
        if include_all_reference_columns:
            for col in GeographicLevels.__table__.columns:
                if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                    columns.append(col.label("geographic_levels_" + col.name))
        else:
            columns.append(GeographicLevels.geographic_level_code.label("geographic_levels_geographic_level_code"))
            columns.append(GeographicLevels.geographic_level.label("geographic_levels_geographic_level"))
        if include_all_reference_columns:
            for col in FoodGroups.__table__.columns:
                if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                    columns.append(col.label("food_groups_" + col.name))
        else:
            columns.append(FoodGroups.food_group_code.label("food_groups_food_group_code"))
            columns.append(FoodGroups.food_group.label("food_groups_food_group"))
        if include_all_reference_columns:
            for col in Indicators.__table__.columns:
                if col.name not in ['id', 'created_at', 'updated_at', 'source_dataset']:
                    columns.append(col.label("indicators_" + col.name))
        else:
            columns.append(Indicators.indicator_code.label("indicators_indicator_code"))
            columns.append(Indicators.indicator.label("indicators_indicator"))
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
    query = select(*columns).select_from(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet)
    
    # Add joins
    query = query.outerjoin(Surveys, HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.survey_code_id == Surveys.id)
    query = query.outerjoin(GeographicLevels, HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.geographic_level_code_id == GeographicLevels.id)
    query = query.outerjoin(FoodGroups, HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.food_group_code_id == FoodGroups.id)
    query = query.outerjoin(Indicators, HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.indicator_code_id == Indicators.id)
    query = query.outerjoin(Elements, HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.element_code_id == Elements.id)
    query = query.outerjoin(Flags, HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.flag_id == Flags.id)
    
    # Build filter conditions for both main query and count query
    conditions = []
    
    # Apply foreign key filters
    if survey_code:
        conditions.append(Surveys.survey_code == survey_code)
    if survey:
        conditions.append(Surveys.survey.ilike("%" + survey + "%"))
    if geographic_level_code:
        conditions.append(GeographicLevels.geographic_level_code == geographic_level_code)
    if geographic_level:
        conditions.append(GeographicLevels.geographic_level.ilike("%" + geographic_level + "%"))
    if food_group_code:
        conditions.append(FoodGroups.food_group_code == food_group_code)
    if food_group:
        conditions.append(FoodGroups.food_group.ilike("%" + food_group + "%"))
    if indicator_code:
        conditions.append(Indicators.indicator_code == indicator_code)
    if indicator:
        conditions.append(Indicators.indicator.ilike("%" + indicator + "%"))
    if element_code:
        conditions.append(Elements.element_code == element_code)
    if element:
        conditions.append(Elements.element.ilike("%" + element + "%"))
    if flag:
        conditions.append(Flags.flag == flag)
    if description:
        conditions.append(Flags.description.ilike("%" + description + "%"))
    
    # Apply dataset-specific column filters
    if unit is not None:
        conditions.append(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.unit.ilike("%" + unit + "%"))
    if unit_exact is not None:
        conditions.append(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.unit == unit_exact)
    if value is not None:
        conditions.append(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.value == value)
    if value_min is not None:
        conditions.append(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.value >= value_min)
    if value_max is not None:
        conditions.append(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.value <= value_max)
    if note is not None:
        conditions.append(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.note.ilike("%" + note + "%"))
    if note_exact is not None:
        conditions.append(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.note == note_exact)
    
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
                    if hasattr(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet, field_name):
                        order_by_clauses.append(getattr(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet, field_name).desc())
                else:
                    # Ascending order
                    if hasattr(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet, sort_field):
                        order_by_clauses.append(getattr(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet, sort_field))
        
        if order_by_clauses:
            query = query.order_by(*order_by_clauses)
    else:
        # Default ordering by ID for consistent pagination
        query = query.order_by(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.id)
    
    # Get total count with filters applied
    count_query = select(func.count()).select_from(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet)
    
    # Add joins to count query
    count_query = count_query.outerjoin(Surveys, HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.survey_code_id == Surveys.id)
    count_query = count_query.outerjoin(GeographicLevels, HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.geographic_level_code_id == GeographicLevels.id)
    count_query = count_query.outerjoin(FoodGroups, HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.food_group_code_id == FoodGroups.id)
    count_query = count_query.outerjoin(Indicators, HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.indicator_code_id == Indicators.id)
    count_query = count_query.outerjoin(Elements, HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.element_code_id == Elements.id)
    count_query = count_query.outerjoin(Flags, HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.flag_id == Flags.id)
    
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
    base_url = str(router.url_path_for('get_household_consumption_and_expenditure_surveys_food_and_diet'))
    
    # Collect all query parameters
    all_params = {
        'limit': limit,
        'offset': offset,
        'survey_code': survey_code,
        'survey': survey,
        'geographic_level_code': geographic_level_code,
        'geographic_level': geographic_level,
        'food_group_code': food_group_code,
        'food_group': food_group,
        'indicator_code': indicator_code,
        'indicator': indicator,
        'element_code': element_code,
        'element': element,
        'flag': flag,
        'description': description,
        'unit': unit,
        'unit_exact': unit_exact,
        'value': value,
        'value_min': value_min,
        'value_max': value_max,
        'note': note,
        'note_exact': note_exact,
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




@router.get("/surveys")
@cache_result(prefix="household_consumption_and_expenditure_surveys_food_and_diet:surveys", ttl=604800)
def get_available_surveys(db: Session = Depends(get_db)):
    """Get all surveys in this dataset"""
    query = (
        select(
            Surveys.survey_code,
            Surveys.survey
        )
        .where(Surveys.source_dataset == 'household_consumption_and_expenditure_surveys_food_and_diet')
        .order_by(Surveys.survey_code)
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "household_consumption_and_expenditure_surveys_food_and_diet",
        "total_surveys": len(results),
        "surveys": [
            {
                "survey_code": r.survey_code,
                "survey": r.survey
            }
            for r in results
        ]
    }




@router.get("/geographic_levels")
@cache_result(prefix="household_consumption_and_expenditure_surveys_food_and_diet:geographic_levels", ttl=604800)
def get_available_geographic_levels(db: Session = Depends(get_db)):
    """Get all geographic levels in this dataset"""
    query = (
        select(
            GeographicLevels.geographic_level_code,
            GeographicLevels.geographic_level
        )
        .where(GeographicLevels.source_dataset == 'household_consumption_and_expenditure_surveys_food_and_diet')
        .order_by(GeographicLevels.geographic_level_code)
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "household_consumption_and_expenditure_surveys_food_and_diet",
        "total_geographic_levels": len(results),
        "geographic_levels": [
            {
                "geographic_level_code": r.geographic_level_code,
                "geographic_level": r.geographic_level
            }
            for r in results
        ]
    }




@router.get("/food_groups")
@cache_result(prefix="household_consumption_and_expenditure_surveys_food_and_diet:food_groups", ttl=604800)
def get_available_food_groups(db: Session = Depends(get_db)):
    """Get all food groups in this dataset"""
    query = (
        select(
            FoodGroups.food_group_code,
            FoodGroups.food_group
        )
        .where(FoodGroups.source_dataset == 'household_consumption_and_expenditure_surveys_food_and_diet')
        .order_by(FoodGroups.food_group_code)
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "household_consumption_and_expenditure_surveys_food_and_diet",
        "total_food_groups": len(results),
        "food_groups": [
            {
                "food_group_code": r.food_group_code,
                "food_group": r.food_group
            }
            for r in results
        ]
    }




@router.get("/indicators")
@cache_result(prefix="household_consumption_and_expenditure_surveys_food_and_diet:indicators", ttl=604800)
def get_available_indicators(db: Session = Depends(get_db)):
    """Get all indicators in this dataset"""
    query = (
        select(
            Indicators.indicator_code,
            Indicators.indicator
        )
        .where(Indicators.source_dataset == 'household_consumption_and_expenditure_surveys_food_and_diet')
        .order_by(Indicators.indicator_code)
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "household_consumption_and_expenditure_surveys_food_and_diet",
        "total_indicators": len(results),
        "indicators": [
            {
                "indicator_code": r.indicator_code,
                "indicator": r.indicator
            }
            for r in results
        ]
    }


@router.get("/elements")
@cache_result(prefix="household_consumption_and_expenditure_surveys_food_and_diet:elements", ttl=604800)
def get_available_elements(db: Session = Depends(get_db)):
    """Get all elements (measures/indicators) in this dataset"""
    query = (
        select(
            Elements.element_code,  
            Elements.element
        )
        .where(Elements.source_dataset == 'household_consumption_and_expenditure_surveys_food_and_diet')
        .order_by(Elements.element_code)
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "household_consumption_and_expenditure_surveys_food_and_diet",
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
@cache_result(prefix="household_consumption_and_expenditure_surveys_food_and_diet:flags", ttl=604800)
def get_data_quality_summary(db: Session = Depends(get_db)):
    """Get data quality flag distribution for this dataset"""
    query = (
        select(
            Flags.flag,
            Flags.description,
            func.count(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.id).label('record_count')
        )
        .join(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet, Flags.id == HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.flag_id)
        .group_by(Flags.flag, Flags.description)
        .order_by(func.count(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.id).desc())
    )
    
    results = db.execute(query).all()
    
    return {
        "dataset": "household_consumption_and_expenditure_surveys_food_and_diet",
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



@router.get("/summary")
@cache_result(prefix="household_consumption_and_expenditure_surveys_food_and_diet:summary", ttl=604800)
def get_dataset_summary(db: Session = Depends(get_db)):
    """Get comprehensive summary of this dataset"""
    total_records = db.query(func.count(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.id)).scalar()
    
    summary = {
        "dataset": "household_consumption_and_expenditure_surveys_food_and_diet",
        "total_records": total_records,
        "foreign_keys": [
            "surveys",
            "geographic_levels",
            "food_groups",
            "indicators",
            "elements",
            "flags",
        ]
    }
    
    summary["unique_surveys"] = db.query(func.count(func.distinct(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.survey_code_id))).scalar()
    summary["unique_geographic_levels"] = db.query(func.count(func.distinct(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.geographic_level_code_id))).scalar()
    summary["unique_food_groups"] = db.query(func.count(func.distinct(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.food_group_code_id))).scalar()
    summary["unique_indicators"] = db.query(func.count(func.distinct(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.indicator_code_id))).scalar()
    summary["unique_elements"] = db.query(func.count(func.distinct(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.element_code_id))).scalar()
    summary["unique_flags"] = db.query(func.count(func.distinct(HouseholdConsumptionAndExpenditureSurveysFoodAndDiet.flag_id))).scalar()
    
    return summary
