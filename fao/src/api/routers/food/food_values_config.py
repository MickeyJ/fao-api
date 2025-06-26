# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/food_values_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.food_values.food_values_model import FoodValues

from fao.src.core.validation import (
    is_valid_food_value_code,
)
from fao.src.core.exceptions import (
    invalid_food_value_code,
)

@dataclass
class FoodValuesConfig:
    """Configuration for food_values API"""
    
    # Basic info
    name: str = "food_values"
    model_name: str = "FoodValues"
    table_name: str = "food_values"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "food_value_code",
        "food_value",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "food_value_code",
        "food_value",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "food_value_code",
            "filter_type": "multi",
            "filter_model": FoodValues,  # <-- Actual model class
            "filter_column": "food_value_code",
            "validation_func": is_valid_food_value_code,
            "exception_func": invalid_food_value_code,
        },
        {
            "name": "food_value",
            "filter_type": "like",
            "filter_model": FoodValues,  # <-- Actual model class
            "filter_column": "food_value",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": FoodValues,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])