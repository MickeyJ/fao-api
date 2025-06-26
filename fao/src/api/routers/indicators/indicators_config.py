# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/indicators_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.indicators.indicators_model import Indicators

from fao.src.core.validation import (
    is_valid_indicator_code,
)
from fao.src.core.exceptions import (
    invalid_indicator_code,
)

@dataclass
class IndicatorsConfig:
    """Configuration for indicators API"""
    
    # Basic info
    name: str = "indicators"
    model_name: str = "Indicators"
    table_name: str = "indicators"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "indicator_code",
        "indicator",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "indicator_code",
        "indicator",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "indicator_code",
            "filter_type": "multi",
            "filter_model": Indicators,  # <-- Actual model class
            "filter_column": "indicator_code",
            "validation_func": is_valid_indicator_code,
            "exception_func": invalid_indicator_code,
        },
        {
            "name": "indicator",
            "filter_type": "like",
            "filter_model": Indicators,  # <-- Actual model class
            "filter_column": "indicator",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": Indicators,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])