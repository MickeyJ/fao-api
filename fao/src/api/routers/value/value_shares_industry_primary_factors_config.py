# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/value_shares_industry_primary_factors_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.value_shares_industry_primary_factors.value_shares_industry_primary_factors_model import ValueSharesIndustryPrimaryFactors
from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes
from fao.src.db.pipelines.food_values.food_values_model import FoodValues
from fao.src.db.pipelines.industries.industries_model import Industries
from fao.src.db.pipelines.factors.factors_model import Factors
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

from fao.src.core.validation import (
    is_valid_area_code,
    is_valid_element_code,
    is_valid_factor_code,
    is_valid_flag,
    is_valid_food_value_code,
    is_valid_industry_code,
)
from fao.src.core.exceptions import (
    invalid_area_code,
    invalid_element_code,
    invalid_factor_code,
    invalid_flag,
    invalid_food_value_code,
    invalid_industry_code,
)

@dataclass
class ValueSharesIndustryPrimaryFactorsConfig:
    """Configuration for value_shares_industry_primary_factors API"""
    
    # Basic info
    name: str = "value_shares_industry_primary_factors"
    model_name: str = "ValueSharesIndustryPrimaryFactors"
    table_name: str = "value_shares_industry_primary_factors"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "area_code",
        "area_code_m49",
        "area",
        "food_value_code",
        "food_value",
        "industry_code",
        "industry",
        "factor_code",
        "factor",
        "element_code",
        "element",
        "year_code",
        "year",
        "unit",
        "value",
        "flag",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "area_code",
        "area",
        "food_value_code",
        "food_value",
        "industry_code",
        "industry",
        "factor_code",
        "factor",
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
            "table_name": "food_values",
            "model_name": "FoodValues",
            "join_column": "food_value_code_id",
            "columns": ["food_value_code", "food_value"],
        },
        {
            "table_name": "industries",
            "model_name": "Industries",
            "join_column": "industry_code_id",
            "columns": ["industry_code", "industry"],
        },
        {
            "table_name": "factors",
            "model_name": "Factors",
            "join_column": "factor_code_id",
            "columns": ["factor_code", "factor"],
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
            "join_condition": ValueSharesIndustryPrimaryFactors.area_code_id,
        },
        {
            "name": "area",
            "filter_type": "like",
            "filter_model": AreaCodes,  # <-- Actual model class
            "filter_column": "area",
            "joins_table": "area_code_id",
            "join_model": AreaCodes,  # <-- Actual model class
            "join_condition": ValueSharesIndustryPrimaryFactors.area_code_id,
        },
        {
            "name": "food_value_code",
            "filter_type": "multi",
            "filter_model": FoodValues,  # <-- Actual model class
            "filter_column": "food_value_code",
            "validation_func": is_valid_food_value_code,
            "exception_func": invalid_food_value_code,
            "joins_table": "food_value_code_id",
            "join_model": FoodValues,  # <-- Actual model class
            "join_condition": ValueSharesIndustryPrimaryFactors.food_value_code_id,
        },
        {
            "name": "food_value",
            "filter_type": "like",
            "filter_model": FoodValues,  # <-- Actual model class
            "filter_column": "food_value",
            "joins_table": "food_value_code_id",
            "join_model": FoodValues,  # <-- Actual model class
            "join_condition": ValueSharesIndustryPrimaryFactors.food_value_code_id,
        },
        {
            "name": "industry_code",
            "filter_type": "multi",
            "filter_model": Industries,  # <-- Actual model class
            "filter_column": "industry_code",
            "validation_func": is_valid_industry_code,
            "exception_func": invalid_industry_code,
            "joins_table": "industry_code_id",
            "join_model": Industries,  # <-- Actual model class
            "join_condition": ValueSharesIndustryPrimaryFactors.industry_code_id,
        },
        {
            "name": "industry",
            "filter_type": "like",
            "filter_model": Industries,  # <-- Actual model class
            "filter_column": "industry",
            "joins_table": "industry_code_id",
            "join_model": Industries,  # <-- Actual model class
            "join_condition": ValueSharesIndustryPrimaryFactors.industry_code_id,
        },
        {
            "name": "factor_code",
            "filter_type": "multi",
            "filter_model": Factors,  # <-- Actual model class
            "filter_column": "factor_code",
            "validation_func": is_valid_factor_code,
            "exception_func": invalid_factor_code,
            "joins_table": "factor_code_id",
            "join_model": Factors,  # <-- Actual model class
            "join_condition": ValueSharesIndustryPrimaryFactors.factor_code_id,
        },
        {
            "name": "factor",
            "filter_type": "like",
            "filter_model": Factors,  # <-- Actual model class
            "filter_column": "factor",
            "joins_table": "factor_code_id",
            "join_model": Factors,  # <-- Actual model class
            "join_condition": ValueSharesIndustryPrimaryFactors.factor_code_id,
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
            "join_condition": ValueSharesIndustryPrimaryFactors.element_code_id,
        },
        {
            "name": "element",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element",
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": ValueSharesIndustryPrimaryFactors.element_code_id,
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
            "join_condition": ValueSharesIndustryPrimaryFactors.flag_id,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": ValueSharesIndustryPrimaryFactors.flag_id,
        },
        {
            "name": "year_code",
            "filter_type": "like",
            "filter_model": ValueSharesIndustryPrimaryFactors,  # <-- Actual model class
            "filter_column": "year_code",
        },
        {
            "name": "year",
            "filter_type": "exact",
            "filter_model": ValueSharesIndustryPrimaryFactors,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_min",
            "filter_type": "range_min",
            "filter_model": ValueSharesIndustryPrimaryFactors,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_max",
            "filter_type": "range_max",
            "filter_model": ValueSharesIndustryPrimaryFactors,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "unit",
            "filter_type": "like",
            "filter_model": ValueSharesIndustryPrimaryFactors,  # <-- Actual model class
            "filter_column": "unit",
        },
        {
            "name": "value",
            "filter_type": "exact",
            "filter_model": ValueSharesIndustryPrimaryFactors,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_min",
            "filter_type": "range_min",
            "filter_model": ValueSharesIndustryPrimaryFactors,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_max",
            "filter_type": "range_max",
            "filter_model": ValueSharesIndustryPrimaryFactors,  # <-- Actual model class
            "filter_column": "value",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "param_name": "year",
            "filter_model": ValueSharesIndustryPrimaryFactors,
            "filter_column": "year",
        },
        {
            "param_name": "value",
            "filter_model": ValueSharesIndustryPrimaryFactors,
            "filter_column": "value",
        },
    ])