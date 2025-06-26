# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/releases_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.releases.releases_model import Releases

from fao.src.core.validation import (
    is_valid_release_code,
)
from fao.src.core.exceptions import (
    invalid_release_code,
)

@dataclass
class ReleasesConfig:
    """Configuration for releases API"""
    
    # Basic info
    name: str = "releases"
    model_name: str = "Releases"
    table_name: str = "releases"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "release_code",
        "release",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "release_code",
        "release",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "release_code",
            "filter_type": "multi",
            "filter_model": Releases,  # <-- Actual model class
            "filter_column": "release_code",
            "validation_func": is_valid_release_code,
            "exception_func": invalid_release_code,
        },
        {
            "name": "release",
            "filter_type": "like",
            "filter_model": Releases,  # <-- Actual model class
            "filter_column": "release",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": Releases,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])