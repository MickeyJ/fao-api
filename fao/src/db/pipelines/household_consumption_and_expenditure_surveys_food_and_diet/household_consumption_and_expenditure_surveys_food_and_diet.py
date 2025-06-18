import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseDatasetETL
from .household_consumption_and_expenditure_surveys_food_and_diet_model import HouseholdConsumptionAndExpenditureSurveysFoodAndDiet


class HouseholdConsumptionAndExpenditureSurveysFoodAndDietETL(BaseDatasetETL):
    """ETL pipeline for household_consumption_and_expenditure_surveys_food_and_diet dataset"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("Household_Consumption_and_Expenditure_Surveys_Food_and_Diet_E_All_Data_(Normalized)/Household_Consumption_and_Expenditure_Surveys_Food_and_Diet_E_All_Data_(Normalized).csv"),
            model_class=HouseholdConsumptionAndExpenditureSurveysFoodAndDiet,
            table_name="household_consumption_and_expenditure_surveys_food_and_diet",
            exclude_columns=["Element", "Element Code", "Flag", "Food Group", "Food Group Code", "Geographic Level", "Geographic Level Code", "Indicator", "Indicator Code", "Survey", "Survey Code"],
            foreign_keys=[{"csv_column_name": "Survey Code", "exception_func": "invalid_survey_code", "format_methods": [], "hash_columns": ["Survey Code", "source_dataset"], "hash_fk_csv_column_name": "Survey Code_id", "hash_fk_sql_column_name": "survey_code_id", "hash_pk_sql_column_name": "id", "index_hash": "4d7aeb72_surveys", "model_name": "Surveys", "pipeline_name": "surveys", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "survey", "reference_pk_csv_column": "Survey Code", "sql_column_name": "survey_code", "table_name": "surveys", "validation_func": "is_valid_survey_code"}, {"csv_column_name": "Geographic Level Code", "exception_func": "invalid_geographic_level_code", "format_methods": [], "hash_columns": ["Geographic Level Code", "source_dataset"], "hash_fk_csv_column_name": "Geographic Level Code_id", "hash_fk_sql_column_name": "geographic_level_code_id", "hash_pk_sql_column_name": "id", "index_hash": "09fa70b9_geographic_levels", "model_name": "GeographicLevels", "pipeline_name": "geographic_levels", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "geographic_level", "reference_pk_csv_column": "Geographic Level Code", "sql_column_name": "geographic_level_code", "table_name": "geographic_levels", "validation_func": "is_valid_geographic_level_code"}, {"csv_column_name": "Food Group Code", "exception_func": "invalid_food_group_code", "format_methods": [], "hash_columns": ["Food Group Code", "source_dataset"], "hash_fk_csv_column_name": "Food Group Code_id", "hash_fk_sql_column_name": "food_group_code_id", "hash_pk_sql_column_name": "id", "index_hash": "e52c01c7_food_groups", "model_name": "FoodGroups", "pipeline_name": "food_groups", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "food_group", "reference_pk_csv_column": "Food Group Code", "sql_column_name": "food_group_code", "table_name": "food_groups", "validation_func": "is_valid_food_group_code"}, {"csv_column_name": "Indicator Code", "exception_func": "invalid_indicator_code", "format_methods": [], "hash_columns": ["Indicator Code", "source_dataset"], "hash_fk_csv_column_name": "Indicator Code_id", "hash_fk_sql_column_name": "indicator_code_id", "hash_pk_sql_column_name": "id", "index_hash": "8060911c_indicators", "model_name": "Indicators", "pipeline_name": "indicators", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "indicator", "reference_pk_csv_column": "Indicator Code", "sql_column_name": "indicator_code", "table_name": "indicators", "validation_func": "is_valid_indicator_code"}, {"csv_column_name": "Element Code", "exception_func": "invalid_element_code", "format_methods": [], "hash_columns": ["Element Code", "source_dataset"], "hash_fk_csv_column_name": "Element Code_id", "hash_fk_sql_column_name": "element_code_id", "hash_pk_sql_column_name": "id", "index_hash": "1dde63d0_elements", "model_name": "Elements", "pipeline_name": "elements", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "element", "reference_pk_csv_column": "Element Code", "sql_column_name": "element_code", "table_name": "elements", "validation_func": "is_valid_element_code"}, {"csv_column_name": "Flag", "exception_func": "invalid_flag", "format_methods": ["upper"], "hash_columns": ["Flag"], "hash_fk_csv_column_name": "Flag_id", "hash_fk_sql_column_name": "flag_id", "hash_pk_sql_column_name": "id", "index_hash": "3b04dd01_flags", "model_name": "Flags", "pipeline_name": "flags", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "description", "reference_pk_csv_column": "Flag", "sql_column_name": "flag", "table_name": "flags", "validation_func": "is_valid_flag"}]
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dataset-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        # Unit
        df['Unit'] = df['Unit'].astype(str).str.strip().str.replace("'", "")
        # Value
        df['Value'] = df['Value'].astype(str).str.strip().str.replace("'", "")
        df['Value'] = df['Value'].replace({'<0.1': 0.05, 'nan': None})
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        # Note
        df['Note'] = df['Note'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        # Foreign key columns
        record['survey_code_id'] = row['survey_code_id']
        record['geographic_level_code_id'] = row['geographic_level_code_id']
        record['food_group_code_id'] = row['food_group_code_id']
        record['indicator_code_id'] = row['indicator_code_id']
        record['element_code_id'] = row['element_code_id']
        record['flag_id'] = row['flag_id']
        # Data columns
        record['unit'] = row['Unit']
        record['value'] = row['Value']
        record['note'] = row['Note']
        return record


# Module-level functions for backwards compatibility
etl = HouseholdConsumptionAndExpenditureSurveysFoodAndDietETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)