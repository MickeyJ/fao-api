# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/food_aid_shipments_wfp_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.food_aid_shipments_wfp.food_aid_shipments_wfp_model import FoodAidShipmentsWfp
from fao.src.db.pipelines.recipient_country_codes.recipient_country_codes_model import RecipientCountryCodes
from fao.src.db.pipelines.item_codes.item_codes_model import ItemCodes
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

from fao.src.core.validation import (
    is_valid_element_code,
    is_valid_flag,
    is_valid_item_code,
    is_valid_recipient_country_code,
)
from fao.src.core.exceptions import (
    invalid_element_code,
    invalid_flag,
    invalid_item_code,
    invalid_recipient_country_code,
)

@dataclass
class FoodAidShipmentsWfpConfig:
    """Configuration for food_aid_shipments_wfp API"""
    
    # Basic info
    name: str = "food_aid_shipments_wfp"
    model_name: str = "FoodAidShipmentsWfp"
    table_name: str = "food_aid_shipments_wfp"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "recipient_country_code",
        "recipient_country_code_m49",
        "recipient_country",
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
        "recipient_country_code",
        "recipient_country",
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
            "table_name": "recipient_country_codes",
            "model_name": "RecipientCountryCodes",
            "join_column": "recipient_country_code_id",
            "columns": ["recipient_country_code", "recipient_country"],
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
            "name": "recipient_country_code",
            "filter_type": "multi",
            "filter_model": RecipientCountryCodes,  # <-- Actual model class
            "filter_column": "recipient_country_code",
            "validation_func": is_valid_recipient_country_code,
            "exception_func": invalid_recipient_country_code,
            "joins_table": "recipient_country_code_id",
            "join_model": RecipientCountryCodes,  # <-- Actual model class
            "join_condition": FoodAidShipmentsWfp.recipient_country_code_id,
        },
        {
            "name": "recipient_country",
            "filter_type": "like",
            "filter_model": RecipientCountryCodes,  # <-- Actual model class
            "filter_column": "recipient_country",
            "joins_table": "recipient_country_code_id",
            "join_model": RecipientCountryCodes,  # <-- Actual model class
            "join_condition": FoodAidShipmentsWfp.recipient_country_code_id,
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
            "join_condition": FoodAidShipmentsWfp.item_code_id,
        },
        {
            "name": "item",
            "filter_type": "like",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "item",
            "joins_table": "item_code_id",
            "join_model": ItemCodes,  # <-- Actual model class
            "join_condition": FoodAidShipmentsWfp.item_code_id,
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
            "join_condition": FoodAidShipmentsWfp.element_code_id,
        },
        {
            "name": "element",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element",
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": FoodAidShipmentsWfp.element_code_id,
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
            "join_condition": FoodAidShipmentsWfp.flag_id,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": FoodAidShipmentsWfp.flag_id,
        },
        {
            "name": "year_code",
            "filter_type": "like",
            "filter_model": FoodAidShipmentsWfp,  # <-- Actual model class
            "filter_column": "year_code",
        },
        {
            "name": "year",
            "filter_type": "exact",
            "filter_model": FoodAidShipmentsWfp,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_min",
            "filter_type": "range_min",
            "filter_model": FoodAidShipmentsWfp,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_max",
            "filter_type": "range_max",
            "filter_model": FoodAidShipmentsWfp,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "unit",
            "filter_type": "like",
            "filter_model": FoodAidShipmentsWfp,  # <-- Actual model class
            "filter_column": "unit",
        },
        {
            "name": "value",
            "filter_type": "exact",
            "filter_model": FoodAidShipmentsWfp,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_min",
            "filter_type": "range_min",
            "filter_model": FoodAidShipmentsWfp,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_max",
            "filter_type": "range_max",
            "filter_model": FoodAidShipmentsWfp,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "note",
            "filter_type": "like",
            "filter_model": FoodAidShipmentsWfp,  # <-- Actual model class
            "filter_column": "note",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "param_name": "year",
            "filter_model": FoodAidShipmentsWfp,
            "filter_column": "year",
        },
        {
            "param_name": "value",
            "filter_model": FoodAidShipmentsWfp,
            "filter_column": "value",
        },
    ])