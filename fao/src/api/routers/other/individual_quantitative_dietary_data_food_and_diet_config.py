# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/individual_quantitative_dietary_data_food_and_diet_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.individual_quantitative_dietary_data_food_and_diet.individual_quantitative_dietary_data_food_and_diet_model import IndividualQuantitativeDietaryDataFoodAndDiet
from fao.src.db.pipelines.surveys.surveys_model import Surveys
from fao.src.db.pipelines.geographic_levels.geographic_levels_model import GeographicLevels
from fao.src.db.pipelines.population_age_groups.population_age_groups_model import PopulationAgeGroups
from fao.src.db.pipelines.food_groups.food_groups_model import FoodGroups
from fao.src.db.pipelines.indicators.indicators_model import Indicators
from fao.src.db.pipelines.elements.elements_model import Elements
from fao.src.db.pipelines.sexs.sexs_model import Sexs
from fao.src.db.pipelines.flags.flags_model import Flags

from fao.src.core.validation import (
    is_valid_element_code,
    is_valid_flag,
    is_valid_food_group_code,
    is_valid_geographic_level_code,
    is_valid_indicator_code,
    is_valid_population_age_group_code,
    is_valid_sex_code,
    is_valid_survey_code,
)
from fao.src.core.exceptions import (
    invalid_element_code,
    invalid_flag,
    invalid_food_group_code,
    invalid_geographic_level_code,
    invalid_indicator_code,
    invalid_population_age_group_code,
    invalid_sex_code,
    invalid_survey_code,
)

@dataclass
class IndividualQuantitativeDietaryDataFoodAndDietConfig:
    """Configuration for individual_quantitative_dietary_data_food_and_diet API"""
    
    # Basic info
    name: str = "individual_quantitative_dietary_data_food_and_diet"
    model_name: str = "IndividualQuantitativeDietaryDataFoodAndDiet"
    table_name: str = "individual_quantitative_dietary_data_food_and_diet"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "survey_code",
        "survey",
        "geographic_level_code",
        "geographic_level",
        "population_age_group_code",
        "population_age_group",
        "food_group_code",
        "food_group",
        "indicator_code",
        "indicator",
        "element_code",
        "element",
        "sex_code",
        "sex",
        "unit",
        "value",
        "flag",
        "note",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "survey_code",
        "survey",
        "geographic_level_code",
        "geographic_level",
        "population_age_group_code",
        "population_age_group",
        "food_group_code",
        "food_group",
        "indicator_code",
        "indicator",
        "element_code",
        "element",
        "sex_code",
        "sex",
        "flag",
        "description",
        "unit",
        "value",
        "value_min",
        "value_max",
        "note",
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
            "table_name": "geographic_levels",
            "model_name": "GeographicLevels",
            "join_column": "geographic_level_code_id",
            "columns": ["geographic_level_code", "geographic_level"],
        },
        {
            "table_name": "population_age_groups",
            "model_name": "PopulationAgeGroups",
            "join_column": "population_age_group_code_id",
            "columns": ["population_age_group_code", "population_age_group"],
        },
        {
            "table_name": "food_groups",
            "model_name": "FoodGroups",
            "join_column": "food_group_code_id",
            "columns": ["food_group_code", "food_group"],
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
            "table_name": "sexs",
            "model_name": "Sexs",
            "join_column": "sex_code_id",
            "columns": ["sex_code", "sex"],
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
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.survey_code_id,
        },
        {
            "name": "survey",
            "filter_type": "like",
            "filter_model": Surveys,  # <-- Actual model class
            "filter_column": "survey",
            "joins_table": "survey_code_id",
            "join_model": Surveys,  # <-- Actual model class
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.survey_code_id,
        },
        {
            "name": "geographic_level_code",
            "filter_type": "multi",
            "filter_model": GeographicLevels,  # <-- Actual model class
            "filter_column": "geographic_level_code",
            "validation_func": is_valid_geographic_level_code,
            "exception_func": invalid_geographic_level_code,
            "joins_table": "geographic_level_code_id",
            "join_model": GeographicLevels,  # <-- Actual model class
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.geographic_level_code_id,
        },
        {
            "name": "geographic_level",
            "filter_type": "like",
            "filter_model": GeographicLevels,  # <-- Actual model class
            "filter_column": "geographic_level",
            "joins_table": "geographic_level_code_id",
            "join_model": GeographicLevels,  # <-- Actual model class
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.geographic_level_code_id,
        },
        {
            "name": "population_age_group_code",
            "filter_type": "multi",
            "filter_model": PopulationAgeGroups,  # <-- Actual model class
            "filter_column": "population_age_group_code",
            "validation_func": is_valid_population_age_group_code,
            "exception_func": invalid_population_age_group_code,
            "joins_table": "population_age_group_code_id",
            "join_model": PopulationAgeGroups,  # <-- Actual model class
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.population_age_group_code_id,
        },
        {
            "name": "population_age_group",
            "filter_type": "like",
            "filter_model": PopulationAgeGroups,  # <-- Actual model class
            "filter_column": "population_age_group",
            "joins_table": "population_age_group_code_id",
            "join_model": PopulationAgeGroups,  # <-- Actual model class
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.population_age_group_code_id,
        },
        {
            "name": "food_group_code",
            "filter_type": "multi",
            "filter_model": FoodGroups,  # <-- Actual model class
            "filter_column": "food_group_code",
            "validation_func": is_valid_food_group_code,
            "exception_func": invalid_food_group_code,
            "joins_table": "food_group_code_id",
            "join_model": FoodGroups,  # <-- Actual model class
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.food_group_code_id,
        },
        {
            "name": "food_group",
            "filter_type": "like",
            "filter_model": FoodGroups,  # <-- Actual model class
            "filter_column": "food_group",
            "joins_table": "food_group_code_id",
            "join_model": FoodGroups,  # <-- Actual model class
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.food_group_code_id,
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
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.indicator_code_id,
        },
        {
            "name": "indicator",
            "filter_type": "like",
            "filter_model": Indicators,  # <-- Actual model class
            "filter_column": "indicator",
            "joins_table": "indicator_code_id",
            "join_model": Indicators,  # <-- Actual model class
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.indicator_code_id,
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
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.element_code_id,
        },
        {
            "name": "element",
            "filter_type": "like",
            "filter_model": Elements,  # <-- Actual model class
            "filter_column": "element",
            "joins_table": "element_code_id",
            "join_model": Elements,  # <-- Actual model class
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.element_code_id,
        },
        {
            "name": "sex_code",
            "filter_type": "multi",
            "filter_model": Sexs,  # <-- Actual model class
            "filter_column": "sex_code",
            "validation_func": is_valid_sex_code,
            "exception_func": invalid_sex_code,
            "joins_table": "sex_code_id",
            "join_model": Sexs,  # <-- Actual model class
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.sex_code_id,
        },
        {
            "name": "sex",
            "filter_type": "like",
            "filter_model": Sexs,  # <-- Actual model class
            "filter_column": "sex",
            "joins_table": "sex_code_id",
            "join_model": Sexs,  # <-- Actual model class
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.sex_code_id,
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
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.flag_id,
        },
        {
            "name": "description",
            "filter_type": "like",
            "filter_model": Flags,  # <-- Actual model class
            "filter_column": "description",
            "joins_table": "flag_id",
            "join_model": Flags,  # <-- Actual model class
            "join_condition": IndividualQuantitativeDietaryDataFoodAndDiet.flag_id,
        },
        {
            "name": "unit",
            "filter_type": "like",
            "filter_model": IndividualQuantitativeDietaryDataFoodAndDiet,  # <-- Actual model class
            "filter_column": "unit",
        },
        {
            "name": "value",
            "filter_type": "exact",
            "filter_model": IndividualQuantitativeDietaryDataFoodAndDiet,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_min",
            "filter_type": "range_min",
            "filter_model": IndividualQuantitativeDietaryDataFoodAndDiet,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "value_max",
            "filter_type": "range_max",
            "filter_model": IndividualQuantitativeDietaryDataFoodAndDiet,  # <-- Actual model class
            "filter_column": "value",
        },
        {
            "name": "note",
            "filter_type": "like",
            "filter_model": IndividualQuantitativeDietaryDataFoodAndDiet,  # <-- Actual model class
            "filter_column": "note",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "param_name": "value",
            "filter_model": IndividualQuantitativeDietaryDataFoodAndDiet,
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
        "geographic_level_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "geographic_level": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "population_age_group_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "population_age_group": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "food_group_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "food_group": {
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
        "sex_code": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "sex": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
        "unit": {
            "type": "String",
            "is_numeric": False,
            "nullable": True,
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
        "note": {
            "type": "String",
            "is_numeric": False,
            "nullable": False,
        },
    })