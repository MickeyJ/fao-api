# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/sexs_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.sexs.sexs_model import Sexs

from fao.src.core.validation import (
    is_valid_sex_code,
)
from fao.src.core.exceptions import (
    invalid_sex_code,
)

@dataclass
class SexsConfig:
    """Configuration for sexs API"""
    
    # Basic info
    name: str = "sexs"
    model_name: str = "Sexs"
    table_name: str = "sexs"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "sex_code",
        "sex",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "sex_code",
        "sex",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "sex_code",
            "filter_type": "multi",
            "filter_model": Sexs,  # <-- Actual model class
            "filter_column": "sex_code",
            "validation_func": is_valid_sex_code,
            "exception_func": invalid_sex_code,
        },
        {
            "name": "sex",
            "filter_type": "like",
            "filter_model": Sexs,  # <-- Actual model class
            "filter_column": "sex",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": Sexs,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])