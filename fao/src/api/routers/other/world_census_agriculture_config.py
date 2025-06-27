# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/world_census_agriculture_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.world_census_agriculture.world_census_agriculture_model import WorldCensusAgriculture
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
class WorldCensusAgricultureConfig:
    """Configuration for world_census_agriculture API"""
    
    # Basic info
    name: str = "world_census_agriculture"
    model_name: str = "WorldCensusAgriculture"
    table_name: str = "world_census_agriculture"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "area_code",
        "area_code_m49",
        "area",
        "item_code",
        "item",
        "element_code",
        "element",
        "wca_round_code",
        "wca_round",
        "census_year_code",
        "census_year",
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
        "wca_round_code",
        "wca_round",
        "wca_round_min",
        "wca_round_max",
        "census_year_code",
        "census_year",
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
            "join_condition": WorldCensusAgriculture.area_code_id,
        },
        {
            "name": "area",
            "filter_type": "like",
            "filter_model": AreaCodes,  # <-- Actual model class
            "filter_column": "area",
            "joins_table": "area_code_id",
            "join_model": AreaCodes,  # <-- Actual model class
            "join_condition": WorldCensusAgriculture.area_code_id,
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
            "join_condition": WorldCensusAgriculture.item_code_id,
        },
        {
            "name": "item",
            "filter_type": "like",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "item",
            "joins_table": "item_code_id",
            "join_model": ItemCodes,  # <-- Actual model class
            "join_condition": WorldCensusAgriculture.item_code_id,
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
            "join_condition": WorldCensusAgriculture.element_code_id,
        },
        {
            "name": "element",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element",
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": WorldCensusAgriculture.element_code_id,
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
            "join_condition": WorldCensusAgriculture.flag_id,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": WorldCensusAgriculture.flag_id,
        },
        {
            "name": "wca_round_code",
            "filter_type": "like",
            "filter_model": WorldCensusAgriculture,  # <-- Actual model class
            "filter_column": "wca_round_code",
        },
        {
            "name": "wca_round",
            "filter_type": "exact",
            "filter_model": WorldCensusAgriculture,  # <-- Actual model class
            "filter_column": "wca_round",
        },
        {
            "name": "wca_round_min",
            "filter_type": "range_min",
            "filter_model": WorldCensusAgriculture,  # <-- Actual model class
            "filter_column": "wca_round",
        },
        {
            "name": "wca_round_max",
            "filter_type": "range_max",
            "filter_model": WorldCensusAgriculture,  # <-- Actual model class
            "filter_column": "wca_round",
        },
        {
            "name": "census_year_code",
            "filter_type": "like",
            "filter_model": WorldCensusAgriculture,  # <-- Actual model class
            "filter_column": "census_year_code",
        },
        {
            "name": "census_year",
            "filter_type": "like",
            "filter_model": WorldCensusAgriculture,  # <-- Actual model class
            "filter_column": "census_year",
        },
        {
            "name": "unit",
            "filter_type": "like",
            "filter_model": WorldCensusAgriculture,  # <-- Actual model class
            "filter_column": "unit",
        },
        {
            "name": "value",
            "filter_type": "exact",
            "filter_model": WorldCensusAgriculture,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_min",
            "filter_type": "range_min",
            "filter_model": WorldCensusAgriculture,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_max",
            "filter_type": "range_max",
            "filter_model": WorldCensusAgriculture,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "note",
            "filter_type": "like",
            "filter_model": WorldCensusAgriculture,  # <-- Actual model class
            "filter_column": "note",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "param_name": "wca_round",
            "filter_model": WorldCensusAgriculture,
            "filter_column": "wca_round",
        },
        {
            "param_name": "value",
            "filter_model": WorldCensusAgriculture,
            "filter_column": "value",
        },
    ])

    field_metadata: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "area_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "area_code_m49": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "area": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "item_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "item": {
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
        "wca_round_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "wca_round": {
            "type": "Integer",
            "is_numeric": True,
            "nullable": False,
        },
        "census_year_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "census_year": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "unit": {
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
        "note": {
            "type": "String",
            "is_numeric": False,
            "nullable": True,
        },
    })