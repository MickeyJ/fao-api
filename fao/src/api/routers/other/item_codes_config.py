# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/item_codes_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.item_codes.item_codes_model import ItemCodes

from fao.src.core.validation import (
    is_valid_item_code,
)
from fao.src.core.exceptions import (
    invalid_item_code,
)

@dataclass
class ItemCodesConfig:
    """Configuration for item_codes API"""
    
    # Basic info
    name: str = "item_codes"
    model_name: str = "ItemCodes"
    table_name: str = "item_codes"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "item_code",
        "item",
        "item_code_cpc",
        "item_code_fbs",
        "item_code_sdg",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "item_code",
        "item",
        "item_code_cpc",
        "item_code_fbs",
        "item_code_sdg",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "item_code",
            "filter_type": "multi",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "item_code",
            "validation_func": is_valid_item_code,
            "exception_func": invalid_item_code,
        },
        {
            "name": "item",
            "filter_type": "like",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "item",
        },
        {
            "name": "item_code_cpc",
            "filter_type": "like",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "item_code_cpc",
        },
        {
            "name": "item_code_fbs",
            "filter_type": "like",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "item_code_fbs",
        },
        {
            "name": "item_code_sdg",
            "filter_type": "like",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "item_code_sdg",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": ItemCodes,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    field_metadata: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
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
        "item_code_cpc": {
            "type": "String",
            "is_numeric": False,
            "nullable": True,
        },
        "item_code_fbs": {
            "type": "String",
            "is_numeric": False,
            "nullable": True,
        },
        "item_code_sdg": {
            "type": "String",
            "is_numeric": False,
            "nullable": True,
        },
        "source_dataset": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
    })