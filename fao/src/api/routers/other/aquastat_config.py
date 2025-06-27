# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/aquastat_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.aquastat.aquastat_model import Aquastat
from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

from fao.src.core.validation import (
    is_valid_area_code,
    is_valid_element_code,
    is_valid_flag,
)
from fao.src.core.exceptions import (
    invalid_area_code,
    invalid_element_code,
    invalid_flag,
)

@dataclass
class AquastatConfig:
    """Configuration for aquastat API"""
    
    # Basic info
    name: str = "aquastat"
    model_name: str = "Aquastat"
    table_name: str = "aquastat"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "area_code",
        "area",
        "element_code",
        "element",
        "unit",
        "year",
        "year_code",
        "value",
        "flag",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "area_code",
        "area",
        "element_code",
        "element",
        "flag",
        "description",
        "unit",
        "year",
        "year_min",
        "year_max",
        "year_code",
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
            "join_condition": Aquastat.area_code_id,
        },
        {
            "name": "area",
            "filter_type": "like",
            "filter_model": AreaCodes,  # <-- Actual model class
            "filter_column": "area",
            "joins_table": "area_code_id",
            "join_model": AreaCodes,  # <-- Actual model class
            "join_condition": Aquastat.area_code_id,
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
            "join_condition": Aquastat.element_code_id,
        },
        {
            "name": "element",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element",
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": Aquastat.element_code_id,
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
            "join_condition": Aquastat.flag_id,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": Aquastat.flag_id,
        },
        {
            "name": "unit",
            "filter_type": "like",
            "filter_model": Aquastat,  # <-- Actual model class
            "filter_column": "unit",
        },
        {
            "name": "year",
            "filter_type": "exact",
            "filter_model": Aquastat,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_min",
            "filter_type": "range_min",
            "filter_model": Aquastat,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_max",
            "filter_type": "range_max",
            "filter_model": Aquastat,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_code",
            "filter_type": "like",
            "filter_model": Aquastat,  # <-- Actual model class
            "filter_column": "year_code",
        },
        {
            "name": "value",
            "filter_type": "exact",
            "filter_model": Aquastat,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_min",
            "filter_type": "range_min",
            "filter_model": Aquastat,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_max",
            "filter_type": "range_max",
            "filter_model": Aquastat,  # <-- Actual model class
            "filter_column": "value",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "param_name": "year",
            "filter_model": Aquastat,
            "filter_column": "year",
        },
        {
            "param_name": "value",
            "filter_model": Aquastat,
            "filter_column": "value",
        },
    ])

    field_metadata: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "area_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "area": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "element_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "element": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "unit": {
            "type": "String",
            "is_numeric": False,
            "nullable": True,
        },
        "year": {
            "type": "SmallInteger",
            "is_numeric": True,
            "nullable": False,
        },
        "year_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "value": {
            "type": "Float",
            "is_numeric": True,
            "nullable": False,
        },
        "flag": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
    })