# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/donors_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.donors.donors_model import Donors

from fao.src.core.validation import (
    is_valid_donor_code,
)
from fao.src.core.exceptions import (
    invalid_donor_code,
)

@dataclass
class DonorsConfig:
    """Configuration for donors API"""
    
    # Basic info
    name: str = "donors"
    model_name: str = "Donors"
    table_name: str = "donors"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "donor_code",
        "donor",
        "donor_code_m49",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "donor_code",
        "donor",
        "donor_code_m49",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "donor_code",
            "filter_type": "multi",
            "filter_model": Donors,  # <-- Actual model class
            "filter_column": "donor_code",
            "validation_func": is_valid_donor_code,
            "exception_func": invalid_donor_code,
        },
        {
            "name": "donor",
            "filter_type": "like",
            "filter_model": Donors,  # <-- Actual model class
            "filter_column": "donor",
        },
        {
            "name": "donor_code_m49",
            "filter_type": "like",
            "filter_model": Donors,  # <-- Actual model class
            "filter_column": "donor_code_m49",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": Donors,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])