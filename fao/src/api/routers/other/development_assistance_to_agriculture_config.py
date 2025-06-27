# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/development_assistance_to_agriculture_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.development_assistance_to_agriculture.development_assistance_to_agriculture_model import DevelopmentAssistanceToAgriculture
from fao.src.db.pipelines.donors.donors_model import Donors
from fao.src.db.pipelines.recipient_country_codes.recipient_country_codes_model import RecipientCountryCodes
from fao.src.db.pipelines.item_codes.item_codes_model import ItemCodes
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.purposes.purposes_model import Purposes
from fao.src.db.pipelines.flags.flags_model import Flags

from fao.src.core.validation import (
    is_valid_donor_code,
    is_valid_element_code,
    is_valid_flag,
    is_valid_item_code,
    is_valid_purpose_code,
    is_valid_recipient_country_code,
)
from fao.src.core.exceptions import (
    invalid_donor_code,
    invalid_element_code,
    invalid_flag,
    invalid_item_code,
    invalid_purpose_code,
    invalid_recipient_country_code,
)

@dataclass
class DevelopmentAssistanceToAgricultureConfig:
    """Configuration for development_assistance_to_agriculture API"""
    
    # Basic info
    name: str = "development_assistance_to_agriculture"
    model_name: str = "DevelopmentAssistanceToAgriculture"
    table_name: str = "development_assistance_to_agriculture"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "donor_code",
        "donor_code_m49",
        "donor",
        "recipient_country_code",
        "recipient_country_code_m49",
        "recipient_country",
        "item_code",
        "item",
        "element_code",
        "element",
        "purpose_code",
        "purpose",
        "year_code",
        "year",
        "unit",
        "value",
        "flag",
        "note",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "donor_code",
        "donor",
        "recipient_country_code",
        "recipient_country",
        "item_code",
        "item",
        "element_code",
        "element",
        "purpose_code",
        "purpose",
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
            "table_name": "donors",
            "model_name": "Donors",
            "join_column": "donor_code_id",
            "columns": ["donor_code", "donor"],
        },
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
            "table_name": "purposes",
            "model_name": "Purposes",
            "join_column": "purpose_code_id",
            "columns": ["purpose_code", "purpose"],
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
            "name": "donor_code",
            "filter_type": "multi",
            "filter_model": Donors,  # <-- Actual model class
            "filter_column": "donor_code",
            "validation_func": is_valid_donor_code,
            "exception_func": invalid_donor_code,
            "joins_table": "donor_code_id",
            "join_model": Donors,  # <-- Actual model class
            "join_condition": DevelopmentAssistanceToAgriculture.donor_code_id,
        },
        {
            "name": "donor",
            "filter_type": "like",
            "filter_model": Donors,  # <-- Actual model class
            "filter_column": "donor",
            "joins_table": "donor_code_id",
            "join_model": Donors,  # <-- Actual model class
            "join_condition": DevelopmentAssistanceToAgriculture.donor_code_id,
        },
        {
            "name": "recipient_country_code",
            "filter_type": "multi",
            "filter_model": RecipientCountryCodes,  # <-- Actual model class
            "filter_column": "recipient_country_code",
            "validation_func": is_valid_recipient_country_code,
            "exception_func": invalid_recipient_country_code,
            "joins_table": "recipient_country_code_id",
            "join_model": RecipientCountryCodes,  # <-- Actual model class
            "join_condition": DevelopmentAssistanceToAgriculture.recipient_country_code_id,
        },
        {
            "name": "recipient_country",
            "filter_type": "like",
            "filter_model": RecipientCountryCodes,  # <-- Actual model class
            "filter_column": "recipient_country",
            "joins_table": "recipient_country_code_id",
            "join_model": RecipientCountryCodes,  # <-- Actual model class
            "join_condition": DevelopmentAssistanceToAgriculture.recipient_country_code_id,
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
            "join_condition": DevelopmentAssistanceToAgriculture.item_code_id,
        },
        {
            "name": "item",
            "filter_type": "like",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "item",
            "joins_table": "item_code_id",
            "join_model": ItemCodes,  # <-- Actual model class
            "join_condition": DevelopmentAssistanceToAgriculture.item_code_id,
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
            "join_condition": DevelopmentAssistanceToAgriculture.element_code_id,
        },
        {
            "name": "element",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element",
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": DevelopmentAssistanceToAgriculture.element_code_id,
        },
        {
            "name": "purpose_code",
            "filter_type": "multi",
            "filter_model": Purposes,  # <-- Actual model class
            "filter_column": "purpose_code",
            "validation_func": is_valid_purpose_code,
            "exception_func": invalid_purpose_code,
            "joins_table": "purpose_code_id",
            "join_model": Purposes,  # <-- Actual model class
            "join_condition": DevelopmentAssistanceToAgriculture.purpose_code_id,
        },
        {
            "name": "purpose",
            "filter_type": "like",
            "filter_model": Purposes,  # <-- Actual model class
            "filter_column": "purpose",
            "joins_table": "purpose_code_id",
            "join_model": Purposes,  # <-- Actual model class
            "join_condition": DevelopmentAssistanceToAgriculture.purpose_code_id,
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
            "join_condition": DevelopmentAssistanceToAgriculture.flag_id,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": DevelopmentAssistanceToAgriculture.flag_id,
        },
        {
            "name": "year_code",
            "filter_type": "like",
            "filter_model": DevelopmentAssistanceToAgriculture,  # <-- Actual model class
            "filter_column": "year_code",
        },
        {
            "name": "year",
            "filter_type": "exact",
            "filter_model": DevelopmentAssistanceToAgriculture,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_min",
            "filter_type": "range_min",
            "filter_model": DevelopmentAssistanceToAgriculture,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "year_max",
            "filter_type": "range_max",
            "filter_model": DevelopmentAssistanceToAgriculture,  # <-- Actual model class
            "filter_column": "year",
        },
        {
            "name": "unit",
            "filter_type": "like",
            "filter_model": DevelopmentAssistanceToAgriculture,  # <-- Actual model class
            "filter_column": "unit",
        },
        {
            "name": "value",
            "filter_type": "exact",
            "filter_model": DevelopmentAssistanceToAgriculture,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_min",
            "filter_type": "range_min",
            "filter_model": DevelopmentAssistanceToAgriculture,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_max",
            "filter_type": "range_max",
            "filter_model": DevelopmentAssistanceToAgriculture,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "note",
            "filter_type": "like",
            "filter_model": DevelopmentAssistanceToAgriculture,  # <-- Actual model class
            "filter_column": "note",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "param_name": "year",
            "filter_model": DevelopmentAssistanceToAgriculture,
            "filter_column": "year",
        },
        {
            "param_name": "value",
            "filter_model": DevelopmentAssistanceToAgriculture,
            "filter_column": "value",
        },
    ])

    field_metadata: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "donor_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "donor_code_m49": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "donor": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "recipient_country_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "recipient_country_code_m49": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "recipient_country": {
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
        "purpose_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "purpose": {
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
        "note": {
            "type": "String",
            "is_numeric": False,
            "nullable": True,
        },
    })