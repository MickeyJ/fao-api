# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/trade_crops_livestock_indicators_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.trade_crops_livestock_indicators.trade_crops_livestock_indicators_model import TradeCropsLivestockIndicators
from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes
from fao.src.db.pipelines.item_codes.item_codes_model import ItemCodes
from fao.src.db.pipelines.indicators.indicators_model import Indicators
from fao.src.db.pipelines.flags.flags_model import Flags

from fao.src.core.validation import (
    is_valid_area_code,
    is_valid_flag,
    is_valid_indicator_code,
    is_valid_item_code,
)
from fao.src.core.exceptions import (
    invalid_area_code,
    invalid_flag,
    invalid_indicator_code,
    invalid_item_code,
)

@dataclass
class TradeCropsLivestockIndicatorsConfig:
    """Configuration for trade_crops_livestock_indicators API"""
    
    # Basic info
    name: str = "trade_crops_livestock_indicators"
    model_name: str = "TradeCropsLivestockIndicators"
    table_name: str = "trade_crops_livestock_indicators"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "area_code",
        "area_code_m49",
        "area",
        "item_code",
        "item_code_cpc",
        "item",
        "indicator_code",
        "indicator",
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
        "indicator_code",
        "indicator",
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
            "table_name": "indicators",
            "model_name": "Indicators",
            "join_column": "indicator_code_id",
            "columns": ["indicator_code", "indicator"],
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
            "join_condition": TradeCropsLivestockIndicators.area_code_id,
        },
        {
            "name": "area",
            "filter_type": "like",
            "filter_model": AreaCodes,  # <-- Actual model class
            "filter_column": "area",
            "joins_table": "area_code_id",
            "join_model": AreaCodes,  # <-- Actual model class
            "join_condition": TradeCropsLivestockIndicators.area_code_id,
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
            "join_condition": TradeCropsLivestockIndicators.item_code_id,
        },
        {
            "name": "item",
            "filter_type": "like",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "item",
            "joins_table": "item_code_id",
            "join_model": ItemCodes,  # <-- Actual model class
            "join_condition": TradeCropsLivestockIndicators.item_code_id,
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
            "join_condition": TradeCropsLivestockIndicators.indicator_code_id,
        },
        {
            "name": "indicator",
            "filter_type": "like",
            "filter_model": Indicators,  # <-- Actual model class
            "filter_column": "indicator",
            "joins_table": "indicator_code_id",
            "join_model": Indicators,  # <-- Actual model class
            "join_condition": TradeCropsLivestockIndicators.indicator_code_id,
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
            "join_condition": TradeCropsLivestockIndicators.flag_id,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": TradeCropsLivestockIndicators.flag_id,
        },
        {
            "name": "year_code",
            "filter_type": "like",
            "filter_model": TradeCropsLivestockIndicators,  # <-- Actual model class
            "filter_column": "year_code",
        },
        {
            "name": "year",
            "filter_type": "exact",
            "filter_model": TradeCropsLivestockIndicators,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_min",
            "filter_type": "range_min",
            "filter_model": TradeCropsLivestockIndicators,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_max",
            "filter_type": "range_max",
            "filter_model": TradeCropsLivestockIndicators,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "unit",
            "filter_type": "like",
            "filter_model": TradeCropsLivestockIndicators,  # <-- Actual model class
            "filter_column": "unit",
        },
        {
            "name": "value",
            "filter_type": "exact",
            "filter_model": TradeCropsLivestockIndicators,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_min",
            "filter_type": "range_min",
            "filter_model": TradeCropsLivestockIndicators,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_max",
            "filter_type": "range_max",
            "filter_model": TradeCropsLivestockIndicators,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "note",
            "filter_type": "like",
            "filter_model": TradeCropsLivestockIndicators,  # <-- Actual model class
            "filter_column": "note",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "param_name": "year",
            "filter_model": TradeCropsLivestockIndicators,
            "filter_column": "year",
        },
        {
            "param_name": "value",
            "filter_model": TradeCropsLivestockIndicators,
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
        "item_code_cpc": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "item": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "indicator_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "indicator": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "year_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "year": {
            "type": "SmallInteger",
            "is_numeric": True,
            "nullable": False,
        },
        "unit": {
            "type": "String",
            "is_numeric": False,
            "nullable": True,
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