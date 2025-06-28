# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/elements_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.elements.elements_model import Elements

from fao.src.core.validation import (
    is_valid_element_code,
)
from fao.src.core.exceptions import (
    invalid_element_code,
)

@dataclass
class ElementsConfig:
    """Configuration for elements API"""
    
    # Basic info
    name: str = "elements"
    model_name: str = "Elements"
    table_name: str = "elements"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "element_code",
        "element",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "element_code",
        "element",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "element_code",
            "filter_type": "multi",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element_code",
            "validation_func": is_valid_element_code,
            "exception_func": invalid_element_code,
        },
        {
            "name": "element",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    field_metadata: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
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
        "source_dataset": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
    })