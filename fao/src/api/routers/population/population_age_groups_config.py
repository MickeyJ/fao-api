# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/population_age_groups_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.population_age_groups.population_age_groups_model import PopulationAgeGroups

from fao.src.core.validation import (
    is_valid_population_age_group_code,
)
from fao.src.core.exceptions import (
    invalid_population_age_group_code,
)

@dataclass
class PopulationAgeGroupsConfig:
    """Configuration for population_age_groups API"""
    
    # Basic info
    name: str = "population_age_groups"
    model_name: str = "PopulationAgeGroups"
    table_name: str = "population_age_groups"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "population_age_group_code",
        "population_age_group",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "population_age_group_code",
        "population_age_group",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "population_age_group_code",
            "filter_type": "multi",
            "filter_model": PopulationAgeGroups,  # <-- Actual model class
            "filter_column": "population_age_group_code",
            "validation_func": is_valid_population_age_group_code,
            "exception_func": invalid_population_age_group_code,
        },
        {
            "name": "population_age_group",
            "filter_type": "like",
            "filter_model": PopulationAgeGroups,  # <-- Actual model class
            "filter_column": "population_age_group",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": PopulationAgeGroups,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])