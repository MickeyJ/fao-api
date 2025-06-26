# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/food_groups_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.food_groups.food_groups_model import FoodGroups

from fao.src.core.validation import (
    is_valid_food_group_code,
)
from fao.src.core.exceptions import (
    invalid_food_group_code,
)

@dataclass
class FoodGroupsConfig:
    """Configuration for food_groups API"""
    
    # Basic info
    name: str = "food_groups"
    model_name: str = "FoodGroups"
    table_name: str = "food_groups"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "food_group_code",
        "food_group",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "food_group_code",
        "food_group",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "food_group_code",
            "filter_type": "multi",
            "filter_model": FoodGroups,  # <-- Actual model class
            "filter_column": "food_group_code",
            "validation_func": is_valid_food_group_code,
            "exception_func": invalid_food_group_code,
        },
        {
            "name": "food_group",
            "filter_type": "like",
            "filter_model": FoodGroups,  # <-- Actual model class
            "filter_column": "food_group",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": FoodGroups,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])