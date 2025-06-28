# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/flags_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.flags.flags_model import Flags

from fao.src.core.validation import (
    is_valid_flag,
)
from fao.src.core.exceptions import (
    invalid_flag,
)

@dataclass
class FlagsConfig:
    """Configuration for flags API"""
    
    # Basic info
    name: str = "flags"
    model_name: str = "Flags"
    table_name: str = "flags"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "flag",
        "description",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "flag",
        "description",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "flag",
            "filter_type": "multi",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "flag",
            "validation_func": is_valid_flag,
            "exception_func": invalid_flag,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    field_metadata: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "flag": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "description": {
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