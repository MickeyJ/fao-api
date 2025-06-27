# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/sources_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.sources.sources_model import Sources

from fao.src.core.validation import (
    is_valid_source_code,
)
from fao.src.core.exceptions import (
    invalid_source_code,
)

@dataclass
class SourcesConfig:
    """Configuration for sources API"""
    
    # Basic info
    name: str = "sources"
    model_name: str = "Sources"
    table_name: str = "sources"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "source_code",
        "source",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "source_code",
        "source",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "source_code",
            "filter_type": "multi",
            "filter_model": Sources,  # <-- Actual model class
            "filter_column": "source_code",
            "validation_func": is_valid_source_code,
            "exception_func": invalid_source_code,
        },
        {
            "name": "source",
            "filter_type": "like",
            "filter_model": Sources,  # <-- Actual model class
            "filter_column": "source",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": Sources,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    field_metadata: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "source_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "source": {
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