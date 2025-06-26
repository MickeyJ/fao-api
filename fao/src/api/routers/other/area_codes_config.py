# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/area_codes_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.area_codes.area_codes_model import AreaCodes

from fao.src.core.validation import (
    is_valid_area_code,
)
from fao.src.core.exceptions import (
    invalid_area_code,
)

@dataclass
class AreaCodesConfig:
    """Configuration for area_codes API"""
    
    # Basic info
    name: str = "area_codes"
    model_name: str = "AreaCodes"
    table_name: str = "area_codes"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "area_code",
        "area",
        "area_code_m49",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "area_code",
        "area",
        "area_code_m49",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "area_code",
            "filter_type": "multi",
            "filter_model": AreaCodes,  # <-- Actual model class
            "filter_column": "area_code",
            "validation_func": is_valid_area_code,
            "exception_func": invalid_area_code,
        },
        {
            "name": "area",
            "filter_type": "like",
            "filter_model": AreaCodes,  # <-- Actual model class
            "filter_column": "area",
        },
        {
            "name": "area_code_m49",
            "filter_type": "like",
            "filter_model": AreaCodes,  # <-- Actual model class
            "filter_column": "area_code_m49",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": AreaCodes,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])