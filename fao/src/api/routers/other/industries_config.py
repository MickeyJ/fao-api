# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/industries_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.industries.industries_model import Industries

from fao.src.core.validation import (
    is_valid_industry_code,
)
from fao.src.core.exceptions import (
    invalid_industry_code,
)

@dataclass
class IndustriesConfig:
    """Configuration for industries API"""
    
    # Basic info
    name: str = "industries"
    model_name: str = "Industries"
    table_name: str = "industries"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "industry_code",
        "industry",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "industry_code",
        "industry",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "industry_code",
            "filter_type": "multi",
            "filter_model": Industries,  # <-- Actual model class
            "filter_column": "industry_code",
            "validation_func": is_valid_industry_code,
            "exception_func": invalid_industry_code,
        },
        {
            "name": "industry",
            "filter_type": "like",
            "filter_model": Industries,  # <-- Actual model class
            "filter_column": "industry",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": Industries,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])