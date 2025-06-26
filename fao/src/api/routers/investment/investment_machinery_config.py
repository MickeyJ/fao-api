# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/investment_machinery_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.investment_machinery.investment_machinery_model import InvestmentMachinery
from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes
from fao.src.db.pipelines.item_codes.item_codes_model import ItemCodes
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

from fao.src.core.validation import (
    is_valid_area_code,
    is_valid_element_code,
    is_valid_flag,
    is_valid_item_code,
)
from fao.src.core.exceptions import (
    invalid_area_code,
    invalid_element_code,
    invalid_flag,
    invalid_item_code,
)

@dataclass
class InvestmentMachineryConfig:
    """Configuration for investment_machinery API"""
    
    # Basic info
    name: str = "investment_machinery"
    model_name: str = "InvestmentMachinery"
    table_name: str = "investment_machinery"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "area_code",
        "area_code_m49",
        "area",
        "item_code",
        "item",
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
        "item_code",
        "item",
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
            "table_name": "item_codes",
            "model_name": "ItemCodes",
            "join_column": "item_code_id",
            "columns": ["item_code", "item"],
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
            "join_condition": InvestmentMachinery.area_code_id,
        },
        {
            "name": "area",
            "filter_type": "like",
            "filter_model": AreaCodes,  # <-- Actual model class
            "filter_column": "area",
            "joins_table": "area_code_id",
            "join_model": AreaCodes,  # <-- Actual model class
            "join_condition": InvestmentMachinery.area_code_id,
        },
        {
            "name": "item_code",
            "filter_type": "multi",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "item_code",
            "validation_func": is_valid_item_code,
            "exception_func": invalid_item_code,
            "joins_table": "item_code_id",
            "join_model": ItemCodes,  # <-- Actual model class
            "join_condition": InvestmentMachinery.item_code_id,
        },
        {
            "name": "item",
            "filter_type": "like",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "item",
            "joins_table": "item_code_id",
            "join_model": ItemCodes,  # <-- Actual model class
            "join_condition": InvestmentMachinery.item_code_id,
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
            "join_condition": InvestmentMachinery.element_code_id,
        },
        {
            "name": "element",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element",
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": InvestmentMachinery.element_code_id,
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
            "join_condition": InvestmentMachinery.flag_id,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": InvestmentMachinery.flag_id,
        },
        {
            "name": "year_code",
            "filter_type": "like",
            "filter_model": InvestmentMachinery,  # <-- Actual model class
            "filter_column": "year_code",
        },
        {
            "name": "year",
            "filter_type": "exact",
            "filter_model": InvestmentMachinery,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_min",
            "filter_type": "range_min",
            "filter_model": InvestmentMachinery,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_max",
            "filter_type": "range_max",
            "filter_model": InvestmentMachinery,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "unit",
            "filter_type": "like",
            "filter_model": InvestmentMachinery,  # <-- Actual model class
            "filter_column": "unit",
        },
        {
            "name": "value",
            "filter_type": "exact",
            "filter_model": InvestmentMachinery,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_min",
            "filter_type": "range_min",
            "filter_model": InvestmentMachinery,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_max",
            "filter_type": "range_max",
            "filter_model": InvestmentMachinery,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "note",
            "filter_type": "like",
            "filter_model": InvestmentMachinery,  # <-- Actual model class
            "filter_column": "note",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "param_name": "year",
            "filter_model": InvestmentMachinery,
            "filter_column": "year",
        },
        {
            "param_name": "value",
            "filter_model": InvestmentMachinery,
            "filter_column": "value",
        },
    ])