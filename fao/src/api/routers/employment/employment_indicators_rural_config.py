# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/employment_indicators_rural_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.employment_indicators_rural.employment_indicators_rural_model import EmploymentIndicatorsRural
from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes
from fao.src.db.pipelines.sources.sources_model import Sources
from fao.src.db.pipelines.indicators.indicators_model import Indicators
from fao.src.db.pipelines.sexs.sexs_model import Sexs
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

from fao.src.core.validation import (
    is_valid_area_code,
    is_valid_element_code,
    is_valid_flag,
    is_valid_indicator_code,
    is_valid_sex_code,
    is_valid_source_code,
)
from fao.src.core.exceptions import (
    invalid_area_code,
    invalid_element_code,
    invalid_flag,
    invalid_indicator_code,
    invalid_sex_code,
    invalid_source_code,
)

@dataclass
class EmploymentIndicatorsRuralConfig:
    """Configuration for employment_indicators_rural API"""
    
    # Basic info
    name: str = "employment_indicators_rural"
    model_name: str = "EmploymentIndicatorsRural"
    table_name: str = "employment_indicators_rural"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "area_code",
        "area_code_m49",
        "area",
        "source_code",
        "source",
        "indicator_code",
        "indicator",
        "sex_code",
        "sex",
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
        "source_code",
        "source",
        "indicator_code",
        "indicator",
        "sex_code",
        "sex",
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
            "table_name": "sources",
            "model_name": "Sources",
            "join_column": "source_code_id",
            "columns": ["source_code", "source"],
        },
        {
            "table_name": "indicators",
            "model_name": "Indicators",
            "join_column": "indicator_code_id",
            "columns": ["indicator_code", "indicator"],
        },
        {
            "table_name": "sexs",
            "model_name": "Sexs",
            "join_column": "sex_code_id",
            "columns": ["sex_code", "sex"],
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
            "join_condition": EmploymentIndicatorsRural.area_code_id,
        },
        {
            "name": "area",
            "filter_type": "like",
            "filter_model": AreaCodes,  # <-- Actual model class
            "filter_column": "area",
            "joins_table": "area_code_id",
            "join_model": AreaCodes,  # <-- Actual model class
            "join_condition": EmploymentIndicatorsRural.area_code_id,
        },
        {
            "name": "source_code",
            "filter_type": "multi",
            "filter_model": Sources,  # <-- Actual model class
            "filter_column": "source_code",
            "validation_func": is_valid_source_code,
            "exception_func": invalid_source_code,
            "joins_table": "source_code_id",
            "join_model": Sources,  # <-- Actual model class
            "join_condition": EmploymentIndicatorsRural.source_code_id,
        },
        {
            "name": "source",
            "filter_type": "like",
            "filter_model": Sources,  # <-- Actual model class
            "filter_column": "source",
            "joins_table": "source_code_id",
            "join_model": Sources,  # <-- Actual model class
            "join_condition": EmploymentIndicatorsRural.source_code_id,
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
            "join_condition": EmploymentIndicatorsRural.indicator_code_id,
        },
        {
            "name": "indicator",
            "filter_type": "like",
            "filter_model": Indicators,  # <-- Actual model class
            "filter_column": "indicator",
            "joins_table": "indicator_code_id",
            "join_model": Indicators,  # <-- Actual model class
            "join_condition": EmploymentIndicatorsRural.indicator_code_id,
        },
        {
            "name": "sex_code",
            "filter_type": "multi",
            "filter_model": Sexs,  # <-- Actual model class
            "filter_column": "sex_code",
            "validation_func": is_valid_sex_code,
            "exception_func": invalid_sex_code,
            "joins_table": "sex_code_id",
            "join_model": Sexs,  # <-- Actual model class
            "join_condition": EmploymentIndicatorsRural.sex_code_id,
        },
        {
            "name": "sex",
            "filter_type": "like",
            "filter_model": Sexs,  # <-- Actual model class
            "filter_column": "sex",
            "joins_table": "sex_code_id",
            "join_model": Sexs,  # <-- Actual model class
            "join_condition": EmploymentIndicatorsRural.sex_code_id,
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
            "join_condition": EmploymentIndicatorsRural.element_code_id,
        },
        {
            "name": "element",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element",
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": EmploymentIndicatorsRural.element_code_id,
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
            "join_condition": EmploymentIndicatorsRural.flag_id,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": EmploymentIndicatorsRural.flag_id,
        },
        {
            "name": "year_code",
            "filter_type": "like",
            "filter_model": EmploymentIndicatorsRural,  # <-- Actual model class
            "filter_column": "year_code",
        },
        {
            "name": "year",
            "filter_type": "exact",
            "filter_model": EmploymentIndicatorsRural,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_min",
            "filter_type": "range_min",
            "filter_model": EmploymentIndicatorsRural,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_max",
            "filter_type": "range_max",
            "filter_model": EmploymentIndicatorsRural,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "unit",
            "filter_type": "like",
            "filter_model": EmploymentIndicatorsRural,  # <-- Actual model class
            "filter_column": "unit",
        },
        {
            "name": "value",
            "filter_type": "exact",
            "filter_model": EmploymentIndicatorsRural,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_min",
            "filter_type": "range_min",
            "filter_model": EmploymentIndicatorsRural,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_max",
            "filter_type": "range_max",
            "filter_model": EmploymentIndicatorsRural,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "note",
            "filter_type": "like",
            "filter_model": EmploymentIndicatorsRural,  # <-- Actual model class
            "filter_column": "note",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "param_name": "year",
            "filter_model": EmploymentIndicatorsRural,
            "filter_column": "year",
        },
        {
            "param_name": "value",
            "filter_model": EmploymentIndicatorsRural,
            "filter_column": "value",
        },
    ])