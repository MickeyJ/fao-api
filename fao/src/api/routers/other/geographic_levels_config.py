# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/geographic_levels_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.geographic_levels.geographic_levels_model import GeographicLevels

from fao.src.core.validation import (
    is_valid_geographic_level_code,
)
from fao.src.core.exceptions import (
    invalid_geographic_level_code,
)

@dataclass
class GeographicLevelsConfig:
    """Configuration for geographic_levels API"""
    
    # Basic info
    name: str = "geographic_levels"
    model_name: str = "GeographicLevels"
    table_name: str = "geographic_levels"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "geographic_level_code",
        "geographic_level",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "geographic_level_code",
        "geographic_level",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "geographic_level_code",
            "filter_type": "multi",
            "filter_model": GeographicLevels,  # <-- Actual model class
            "filter_column": "geographic_level_code",
            "validation_func": is_valid_geographic_level_code,
            "exception_func": invalid_geographic_level_code,
        },
        {
            "name": "geographic_level",
            "filter_type": "like",
            "filter_model": GeographicLevels,  # <-- Actual model class
            "filter_column": "geographic_level",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": GeographicLevels,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])