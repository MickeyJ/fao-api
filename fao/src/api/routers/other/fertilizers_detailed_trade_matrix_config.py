# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/fertilizers_detailed_trade_matrix_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.fertilizers_detailed_trade_matrix.fertilizers_detailed_trade_matrix_model import FertilizersDetailedTradeMatrix
from fao.src.db.pipelines.reporter_country_codes.reporter_country_codes_model import ReporterCountryCodes
from fao.src.db.pipelines.partner_country_codes.partner_country_codes_model import PartnerCountryCodes
from fao.src.db.pipelines.item_codes.item_codes_model import ItemCodes
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

from fao.src.core.validation import (
    is_valid_element_code,
    is_valid_flag,
    is_valid_item_code,
    is_valid_partner_country_code,
    is_valid_reporter_country_code,
)
from fao.src.core.exceptions import (
    invalid_element_code,
    invalid_flag,
    invalid_item_code,
    invalid_partner_country_code,
    invalid_reporter_country_code,
)

@dataclass
class FertilizersDetailedTradeMatrixConfig:
    """Configuration for fertilizers_detailed_trade_matrix API"""
    
    # Basic info
    name: str = "fertilizers_detailed_trade_matrix"
    model_name: str = "FertilizersDetailedTradeMatrix"
    table_name: str = "fertilizers_detailed_trade_matrix"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "reporter_country_code",
        "reporter_country_code_m49",
        "reporter_countries",
        "partner_country_code",
        "partner_country_code_m49",
        "partner_countries",
        "item_code",
        "item_code_cpc",
        "item",
        "element_code",
        "element",
        "year_code",
        "year",
        "unit",
        "value",
        "flag",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "reporter_country_code",
        "reporter_countries",
        "partner_country_code",
        "partner_countries",
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
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "table_name": "reporter_country_codes",
            "model_name": "ReporterCountryCodes",
            "join_column": "reporter_country_code_id",
            "columns": ["reporter_country_code", "reporter_countries"],
        },
        {
            "table_name": "partner_country_codes",
            "model_name": "PartnerCountryCodes",
            "join_column": "partner_country_code_id",
            "columns": ["partner_country_code", "partner_countries"],
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
            "name": "reporter_country_code",
            "filter_type": "multi",
            "filter_model": ReporterCountryCodes,  # <-- Actual model class
            "filter_column": "reporter_country_code",
            "validation_func": is_valid_reporter_country_code,
            "exception_func": invalid_reporter_country_code,
            "joins_table": "reporter_country_code_id",
            "join_model": ReporterCountryCodes,  # <-- Actual model class
            "join_condition": FertilizersDetailedTradeMatrix.reporter_country_code_id,
        },
        {
            "name": "reporter_countries",
            "filter_type": "like",
            "filter_model": ReporterCountryCodes,  # <-- Actual model class
            "filter_column": "reporter_countries",
            "joins_table": "reporter_country_code_id",
            "join_model": ReporterCountryCodes,  # <-- Actual model class
            "join_condition": FertilizersDetailedTradeMatrix.reporter_country_code_id,
        },
        {
            "name": "partner_country_code",
            "filter_type": "multi",
            "filter_model": PartnerCountryCodes,  # <-- Actual model class
            "filter_column": "partner_country_code",
            "validation_func": is_valid_partner_country_code,
            "exception_func": invalid_partner_country_code,
            "joins_table": "partner_country_code_id",
            "join_model": PartnerCountryCodes,  # <-- Actual model class
            "join_condition": FertilizersDetailedTradeMatrix.partner_country_code_id,
        },
        {
            "name": "partner_countries",
            "filter_type": "like",
            "filter_model": PartnerCountryCodes,  # <-- Actual model class
            "filter_column": "partner_countries",
            "joins_table": "partner_country_code_id",
            "join_model": PartnerCountryCodes,  # <-- Actual model class
            "join_condition": FertilizersDetailedTradeMatrix.partner_country_code_id,
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
            "join_condition": FertilizersDetailedTradeMatrix.item_code_id,
        },
        {
            "name": "item",
            "filter_type": "like",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "item",
            "joins_table": "item_code_id",
            "join_model": ItemCodes,  # <-- Actual model class
            "join_condition": FertilizersDetailedTradeMatrix.item_code_id,
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
            "join_condition": FertilizersDetailedTradeMatrix.element_code_id,
        },
        {
            "name": "element",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element",
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": FertilizersDetailedTradeMatrix.element_code_id,
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
            "join_condition": FertilizersDetailedTradeMatrix.flag_id,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": FertilizersDetailedTradeMatrix.flag_id,
        },
        {
            "name": "year_code",
            "filter_type": "like",
            "filter_model": FertilizersDetailedTradeMatrix,  # <-- Actual model class
            "filter_column": "year_code",
        },
        {
            "name": "year",
            "filter_type": "exact",
            "filter_model": FertilizersDetailedTradeMatrix,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_min",
            "filter_type": "range_min",
            "filter_model": FertilizersDetailedTradeMatrix,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_max",
            "filter_type": "range_max",
            "filter_model": FertilizersDetailedTradeMatrix,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "unit",
            "filter_type": "like",
            "filter_model": FertilizersDetailedTradeMatrix,  # <-- Actual model class
            "filter_column": "unit",
        },
        {
            "name": "value",
            "filter_type": "exact",
            "filter_model": FertilizersDetailedTradeMatrix,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_min",
            "filter_type": "range_min",
            "filter_model": FertilizersDetailedTradeMatrix,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_max",
            "filter_type": "range_max",
            "filter_model": FertilizersDetailedTradeMatrix,  # <-- Actual model class
            "filter_column": "value",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "param_name": "year",
            "filter_model": FertilizersDetailedTradeMatrix,
            "filter_column": "year",
        },
        {
            "param_name": "value",
            "filter_model": FertilizersDetailedTradeMatrix,
            "filter_column": "value",
        },
    ])

    field_metadata: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "reporter_country_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "reporter_country_code_m49": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "reporter_countries": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "partner_country_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "partner_country_code_m49": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "partner_countries": {
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