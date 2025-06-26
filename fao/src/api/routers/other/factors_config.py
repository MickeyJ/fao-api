# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/factors_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.factors.factors_model import Factors

from fao.src.core.validation import (
    is_valid_factor_code,
)
from fao.src.core.exceptions import (
    invalid_factor_code,
)

@dataclass
class FactorsConfig:
    """Configuration for factors API"""
    
    # Basic info
    name: str = "factors"
    model_name: str = "Factors"
    table_name: str = "factors"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "factor_code",
        "factor",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "factor_code",
        "factor",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "factor_code",
            "filter_type": "multi",
            "filter_model": Factors,  # <-- Actual model class
            "filter_column": "factor_code",
            "validation_func": is_valid_factor_code,
            "exception_func": invalid_factor_code,
        },
        {
            "name": "factor",
            "filter_type": "like",
            "filter_model": Factors,  # <-- Actual model class
            "filter_column": "factor",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": Factors,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])