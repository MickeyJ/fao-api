# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/surveys_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.surveys.surveys_model import Surveys

from fao.src.core.validation import (
    is_valid_survey_code,
)
from fao.src.core.exceptions import (
    invalid_survey_code,
)

@dataclass
class SurveysConfig:
    """Configuration for surveys API"""
    
    # Basic info
    name: str = "surveys"
    model_name: str = "Surveys"
    table_name: str = "surveys"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "survey_code",
        "survey",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "survey_code",
        "survey",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "survey_code",
            "filter_type": "multi",
            "filter_model": Surveys,  # <-- Actual model class
            "filter_column": "survey_code",
            "validation_func": is_valid_survey_code,
            "exception_func": invalid_survey_code,
        },
        {
            "name": "survey",
            "filter_type": "like",
            "filter_model": Surveys,  # <-- Actual model class
            "filter_column": "survey",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": Surveys,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])