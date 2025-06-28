# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/recipient_country_codes_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.recipient_country_codes.recipient_country_codes_model import RecipientCountryCodes

from fao.src.core.validation import (
    is_valid_recipient_country_code,
)
from fao.src.core.exceptions import (
    invalid_recipient_country_code,
)

@dataclass
class RecipientCountryCodesConfig:
    """Configuration for recipient_country_codes API"""
    
    # Basic info
    name: str = "recipient_country_codes"
    model_name: str = "RecipientCountryCodes"
    table_name: str = "recipient_country_codes"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "recipient_country_code",
        "recipient_country",
        "recipient_country_code_m49",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "recipient_country_code",
        "recipient_country",
        "recipient_country_code_m49",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "recipient_country_code",
            "filter_type": "multi",
            "filter_model": RecipientCountryCodes,  # <-- Actual model class
            "filter_column": "recipient_country_code",
            "validation_func": is_valid_recipient_country_code,
            "exception_func": invalid_recipient_country_code,
        },
        {
            "name": "recipient_country",
            "filter_type": "like",
            "filter_model": RecipientCountryCodes,  # <-- Actual model class
            "filter_column": "recipient_country",
        },
        {
            "name": "recipient_country_code_m49",
            "filter_type": "like",
            "filter_model": RecipientCountryCodes,  # <-- Actual model class
            "filter_column": "recipient_country_code_m49",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": RecipientCountryCodes,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    field_metadata: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "recipient_country_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "recipient_country": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "recipient_country_code_m49": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "source_dataset": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
    })