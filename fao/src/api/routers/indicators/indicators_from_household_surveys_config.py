# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/indicators_from_household_surveys_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.indicators_from_household_surveys.indicators_from_household_surveys_model import IndicatorsFromHouseholdSurveys
from fao.src.db.pipelines.surveys.surveys_model import Surveys
from fao.src.db.pipelines.indicators.indicators_model import Indicators
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.flags.flags_model import Flags

from fao.src.core.validation import (
    is_valid_element_code,
    is_valid_flag,
    is_valid_indicator_code,
    is_valid_survey_code,
)
from fao.src.core.exceptions import (
    invalid_element_code,
    invalid_flag,
    invalid_indicator_code,
    invalid_survey_code,
)

@dataclass
class IndicatorsFromHouseholdSurveysConfig:
    """Configuration for indicators_from_household_surveys API"""
    
    # Basic info
    name: str = "indicators_from_household_surveys"
    model_name: str = "IndicatorsFromHouseholdSurveys"
    table_name: str = "indicators_from_household_surveys"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "survey_code",
        "survey",
        "breakdown_variable_code",
        "breakdown_variable",
        "breadown_by_sex_of_the_household_head_code",
        "breadown_by_sex_of_the_household_head",
        "indicator_code",
        "indicator",
        "element_code",
        "element",
        "unit",
        "value",
        "flag",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "survey_code",
        "survey",
        "indicator_code",
        "indicator",
        "element_code",
        "element",
        "flag",
        "description",
        "breakdown_variable_code",
        "breakdown_variable",
        "breadown_by_sex_of_the_household_head_code",
        "breadown_by_sex_of_the_household_head",
        "unit",
        "value",
        "value_min",
        "value_max",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "table_name": "surveys",
            "model_name": "Surveys",
            "join_column": "survey_code_id",
            "columns": ["survey_code", "survey"],
        },
        {
            "table_name": "indicators",
            "model_name": "Indicators",
            "join_column": "indicator_code_id",
            "columns": ["indicator_code", "indicator"],
        },
        {
            "table_name": "elements",
            "model_name": "Elements",
            "join_column": "element_code_id",
            "columns": ["element_code", "element"],
        },
        {
            "table_name": "flags",
            "model_name": "Flags",
            "join_column": "flag_id",
            "columns": ["flag", "description"],
        },
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "survey_code",
            "filter_type": "multi",
            "filter_model": Surveys,  # <-- Actual model class
            "filter_column": "survey_code",
            "validation_func": is_valid_survey_code,
            "exception_func": invalid_survey_code,
            "joins_table": "survey_code_id",
            "join_model": Surveys,  # <-- Actual model class
            "join_condition": IndicatorsFromHouseholdSurveys.survey_code_id,
        },
        {
            "name": "survey",
            "filter_type": "like",
            "filter_model": Surveys,  # <-- Actual model class
            "filter_column": "survey",
            "joins_table": "survey_code_id",
            "join_model": Surveys,  # <-- Actual model class
            "join_condition": IndicatorsFromHouseholdSurveys.survey_code_id,
        },
        {
            "name": "indicator_code",
            "filter_type": "multi",
            "filter_model": Indicators,  # <-- Actual model class
            "filter_column": "indicator_code",
            "validation_func": is_valid_indicator_code,
            "exception_func": invalid_indicator_code,
            "joins_table": "indicator_code_id",
            "join_model": Indicators,  # <-- Actual model class
            "join_condition": IndicatorsFromHouseholdSurveys.indicator_code_id,
        },
        {
            "name": "indicator",
            "filter_type": "like",
            "filter_model": Indicators,  # <-- Actual model class
            "filter_column": "indicator",
            "joins_table": "indicator_code_id",
            "join_model": Indicators,  # <-- Actual model class
            "join_condition": IndicatorsFromHouseholdSurveys.indicator_code_id,
        },
        {
            "name": "element_code",
            "filter_type": "multi",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element_code",
            "validation_func": is_valid_element_code,
            "exception_func": invalid_element_code,
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": IndicatorsFromHouseholdSurveys.element_code_id,
        },
        {
            "name": "element",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element",
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": IndicatorsFromHouseholdSurveys.element_code_id,
        },
        {
            "name": "flag",
            "filter_type": "multi",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "flag",
            "validation_func": is_valid_flag,
            "exception_func": invalid_flag,
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": IndicatorsFromHouseholdSurveys.flag_id,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": IndicatorsFromHouseholdSurveys.flag_id,
        },
        {
            "name": "breakdown_variable_code",
            "filter_type": "like",
            "filter_model": IndicatorsFromHouseholdSurveys,  # <-- Actual model class
            "filter_column": "breakdown_variable_code",
        },
        {
            "name": "breakdown_variable",
            "filter_type": "like",
            "filter_model": IndicatorsFromHouseholdSurveys,  # <-- Actual model class
            "filter_column": "breakdown_variable",
        },
        {
            "name": "breadown_by_sex_of_the_household_head_code",
            "filter_type": "like",
            "filter_model": IndicatorsFromHouseholdSurveys,  # <-- Actual model class
            "filter_column": "breadown_by_sex_of_the_household_head_code",
        },
        {
            "name": "breadown_by_sex_of_the_household_head",
            "filter_type": "like",
            "filter_model": IndicatorsFromHouseholdSurveys,  # <-- Actual model class
            "filter_column": "breadown_by_sex_of_the_household_head",
        },
        {
            "name": "unit",
            "filter_type": "like",
            "filter_model": IndicatorsFromHouseholdSurveys,  # <-- Actual model class
            "filter_column": "unit",
        },
        {
            "name": "value",
            "filter_type": "exact",
            "filter_model": IndicatorsFromHouseholdSurveys,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_min",
            "filter_type": "range_min",
            "filter_model": IndicatorsFromHouseholdSurveys,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_max",
            "filter_type": "range_max",
            "filter_model": IndicatorsFromHouseholdSurveys,  # <-- Actual model class
            "filter_column": "value",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "param_name": "value",
            "filter_model": IndicatorsFromHouseholdSurveys,
            "filter_column": "value",
        },
    ])

    field_metadata: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "survey_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "survey": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "breakdown_variable_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "breakdown_variable": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "breadown_by_sex_of_the_household_head_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "breadown_by_sex_of_the_household_head": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "indicator_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "indicator": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "element_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "element": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "unit": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "value": {
            "type": "Float",
            "is_numeric": True,
            "nullable": False,
        },
        "flag": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
    })