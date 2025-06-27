# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/reporter_country_codes_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.reporter_country_codes.reporter_country_codes_model import ReporterCountryCodes

from fao.src.core.validation import (
    is_valid_reporter_country_code,
)
from fao.src.core.exceptions import (
    invalid_reporter_country_code,
)

@dataclass
class ReporterCountryCodesConfig:
    """Configuration for reporter_country_codes API"""
    
    # Basic info
    name: str = "reporter_country_codes"
    model_name: str = "ReporterCountryCodes"
    table_name: str = "reporter_country_codes"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "reporter_country_code",
        "reporter_countries",
        "reporter_country_code_m49",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "reporter_country_code",
        "reporter_countries",
        "reporter_country_code_m49",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "reporter_country_code",
            "filter_type": "multi",
            "filter_model": ReporterCountryCodes,  # <-- Actual model class
            "filter_column": "reporter_country_code",
            "validation_func": is_valid_reporter_country_code,
            "exception_func": invalid_reporter_country_code,
        },
        {
            "name": "reporter_countries",
            "filter_type": "like",
            "filter_model": ReporterCountryCodes,  # <-- Actual model class
            "filter_column": "reporter_countries",
        },
        {
            "name": "reporter_country_code_m49",
            "filter_type": "like",
            "filter_model": ReporterCountryCodes,  # <-- Actual model class
            "filter_column": "reporter_country_code_m49",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": ReporterCountryCodes,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    field_metadata: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "reporter_country_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "reporter_countries": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "reporter_country_code_m49": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "source_dataset": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
    })