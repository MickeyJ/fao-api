# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/supply_utilization_accounts_food_and_diet_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.supply_utilization_accounts_food_and_diet.supply_utilization_accounts_food_and_diet_model import SupplyUtilizationAccountsFoodAndDiet
from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes
from fao.src.db.pipelines.food_groups.food_groups_model import FoodGroups
from fao.src.db.pipelines.indicators.indicators_model import Indicators
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

from fao.src.core.validation import (
    is_valid_area_code,
    is_valid_element_code,
    is_valid_flag,
    is_valid_food_group_code,
    is_valid_indicator_code,
)
from fao.src.core.exceptions import (
    invalid_area_code,
    invalid_element_code,
    invalid_flag,
    invalid_food_group_code,
    invalid_indicator_code,
)

@dataclass
class SupplyUtilizationAccountsFoodAndDietConfig:
    """Configuration for supply_utilization_accounts_food_and_diet API"""
    
    # Basic info
    name: str = "supply_utilization_accounts_food_and_diet"
    model_name: str = "SupplyUtilizationAccountsFoodAndDiet"
    table_name: str = "supply_utilization_accounts_food_and_diet"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "area_code",
        "area_code_m49",
        "area",
        "food_group_code",
        "food_group",
        "indicator_code",
        "indicator",
        "element_code",
        "element",
        "year_code",
        "year",
        "unit",
        "value",
        "flag",
        "note",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "area_code",
        "area",
        "food_group_code",
        "food_group",
        "indicator_code",
        "indicator",
        "element_code",
        "element",
        "flag",
        "description",
        "year_code",
        "year",
        "year_min",
        "year_max",
        "unit",
        "value",
        "value_min",
        "value_max",
        "note",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "table_name": "area_codes",
            "model_name": "AreaCodes",
            "join_column": "area_code_id",
            "columns": ["area_code", "area"],
        },
        {
            "table_name": "food_groups",
            "model_name": "FoodGroups",
            "join_column": "food_group_code_id",
            "columns": ["food_group_code", "food_group"],
        },
        {
            "table_name": "indicators",
            "model_name": "Indicators",
            "join_column": "indicator_code_id",
            "columns": ["indicator_code", "indicator"],
        },
        {
            "table_name": "elements",
            "model_name": "Elements",
            "join_column": "element_code_id",
            "columns": ["element_code", "element"],
        },
        {
            "table_name": "flags",
            "model_name": "Flags",
            "join_column": "flag_id",
            "columns": ["flag", "description"],
        },
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "area_code",
            "filter_type": "multi",
            "filter_model": AreaCodes,  # <-- Actual model class
            "filter_column": "area_code",
            "validation_func": is_valid_area_code,
            "exception_func": invalid_area_code,
            "joins_table": "area_code_id",
            "join_model": AreaCodes,  # <-- Actual model class
            "join_condition": SupplyUtilizationAccountsFoodAndDiet.area_code_id,
        },
        {
            "name": "area",
            "filter_type": "like",
            "filter_model": AreaCodes,  # <-- Actual model class
            "filter_column": "area",
            "joins_table": "area_code_id",
            "join_model": AreaCodes,  # <-- Actual model class
            "join_condition": SupplyUtilizationAccountsFoodAndDiet.area_code_id,
        },
        {
            "name": "food_group_code",
            "filter_type": "multi",
            "filter_model": FoodGroups,  # <-- Actual model class
            "filter_column": "food_group_code",
            "validation_func": is_valid_food_group_code,
            "exception_func": invalid_food_group_code,
            "joins_table": "food_group_code_id",
            "join_model": FoodGroups,  # <-- Actual model class
            "join_condition": SupplyUtilizationAccountsFoodAndDiet.food_group_code_id,
        },
        {
            "name": "food_group",
            "filter_type": "like",
            "filter_model": FoodGroups,  # <-- Actual model class
            "filter_column": "food_group",
            "joins_table": "food_group_code_id",
            "join_model": FoodGroups,  # <-- Actual model class
            "join_condition": SupplyUtilizationAccountsFoodAndDiet.food_group_code_id,
        },
        {
            "name": "indicator_code",
            "filter_type": "multi",
            "filter_model": Indicators,  # <-- Actual model class
            "filter_column": "indicator_code",
            "validation_func": is_valid_indicator_code,
            "exception_func": invalid_indicator_code,
            "joins_table": "indicator_code_id",
            "join_model": Indicators,  # <-- Actual model class
            "join_condition": SupplyUtilizationAccountsFoodAndDiet.indicator_code_id,
        },
        {
            "name": "indicator",
            "filter_type": "like",
            "filter_model": Indicators,  # <-- Actual model class
            "filter_column": "indicator",
            "joins_table": "indicator_code_id",
            "join_model": Indicators,  # <-- Actual model class
            "join_condition": SupplyUtilizationAccountsFoodAndDiet.indicator_code_id,
        },
        {
            "name": "element_code",
            "filter_type": "multi",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element_code",
            "validation_func": is_valid_element_code,
            "exception_func": invalid_element_code,
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": SupplyUtilizationAccountsFoodAndDiet.element_code_id,
        },
        {
            "name": "element",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element",
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": SupplyUtilizationAccountsFoodAndDiet.element_code_id,
        },
        {
            "name": "flag",
            "filter_type": "multi",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "flag",
            "validation_func": is_valid_flag,
            "exception_func": invalid_flag,
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": SupplyUtilizationAccountsFoodAndDiet.flag_id,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": SupplyUtilizationAccountsFoodAndDiet.flag_id,
        },
        {
            "name": "year_code",
            "filter_type": "like",
            "filter_model": SupplyUtilizationAccountsFoodAndDiet,  # <-- Actual model class
            "filter_column": "year_code",
        },
        {
            "name": "year",
            "filter_type": "exact",
            "filter_model": SupplyUtilizationAccountsFoodAndDiet,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_min",
            "filter_type": "range_min",
            "filter_model": SupplyUtilizationAccountsFoodAndDiet,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_max",
            "filter_type": "range_max",
            "filter_model": SupplyUtilizationAccountsFoodAndDiet,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "unit",
            "filter_type": "like",
            "filter_model": SupplyUtilizationAccountsFoodAndDiet,  # <-- Actual model class
            "filter_column": "unit",
        },
        {
            "name": "value",
            "filter_type": "exact",
            "filter_model": SupplyUtilizationAccountsFoodAndDiet,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_min",
            "filter_type": "range_min",
            "filter_model": SupplyUtilizationAccountsFoodAndDiet,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_max",
            "filter_type": "range_max",
            "filter_model": SupplyUtilizationAccountsFoodAndDiet,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "note",
            "filter_type": "like",
            "filter_model": SupplyUtilizationAccountsFoodAndDiet,  # <-- Actual model class
            "filter_column": "note",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "param_name": "year",
            "filter_model": SupplyUtilizationAccountsFoodAndDiet,
            "filter_column": "year",
        },
        {
            "param_name": "value",
            "filter_model": SupplyUtilizationAccountsFoodAndDiet,
            "filter_column": "value",
        },
    ])