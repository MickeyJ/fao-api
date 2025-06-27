# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/purposes_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.purposes.purposes_model import Purposes

from fao.src.core.validation import (
    is_valid_purpose_code,
)
from fao.src.core.exceptions import (
    invalid_purpose_code,
)

@dataclass
class PurposesConfig:
    """Configuration for purposes API"""
    
    # Basic info
    name: str = "purposes"
    model_name: str = "Purposes"
    table_name: str = "purposes"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "purpose_code",
        "purpose",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "purpose_code",
        "purpose",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "purpose_code",
            "filter_type": "multi",
            "filter_model": Purposes,  # <-- Actual model class
            "filter_column": "purpose_code",
            "validation_func": is_valid_purpose_code,
            "exception_func": invalid_purpose_code,
        },
        {
            "name": "purpose",
            "filter_type": "like",
            "filter_model": Purposes,  # <-- Actual model class
            "filter_column": "purpose",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": Purposes,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    field_metadata: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
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
        "source_dataset": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
    })