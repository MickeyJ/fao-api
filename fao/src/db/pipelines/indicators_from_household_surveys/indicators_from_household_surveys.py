import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseDatasetETL
from .indicators_from_household_surveys_model import IndicatorsFromHouseholdSurveys


class IndicatorsFromHouseholdSurveysETL(BaseDatasetETL):
    """ETL pipeline for indicators_from_household_surveys dataset"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("Indicators_from_Household_Surveys_E_All_Data_(Normalized)/Indicators_from_Household_Surveys_E_All_Data_(Normalized).csv"),
            model_class=IndicatorsFromHouseholdSurveys,
            table_name="indicators_from_household_surveys",
            exclude_columns=["Element", "Element Code", "Flag", "Indicator", "Indicator Code", "Survey", "Survey Code"],
            foreign_keys=[{"csv_column_name": "Survey Code", "exception_func": "invalid_survey_code", "format_methods": [], "hash_columns": ["Survey Code", "source_dataset"], "hash_fk_csv_column_name": "Survey Code_id", "hash_fk_sql_column_name": "survey_code_id", "hash_pk_sql_column_name": "id", "index_hash": "87237df8_surveys", "model_name": "Surveys", "pipeline_name": "surveys", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "survey", "reference_pk_csv_column": "Survey Code", "sql_column_name": "survey_code", "table_name": "surveys", "validation_func": "is_valid_survey_code"}, {"csv_column_name": "Indicator Code", "exception_func": "invalid_indicator_code", "format_methods": [], "hash_columns": ["Indicator Code", "source_dataset"], "hash_fk_csv_column_name": "Indicator Code_id", "hash_fk_sql_column_name": "indicator_code_id", "hash_pk_sql_column_name": "id", "index_hash": "51eaa30f_indicators", "model_name": "Indicators", "pipeline_name": "indicators", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "indicator", "reference_pk_csv_column": "Indicator Code", "sql_column_name": "indicator_code", "table_name": "indicators", "validation_func": "is_valid_indicator_code"}, {"csv_column_name": "Element Code", "exception_func": "invalid_element_code", "format_methods": [], "hash_columns": ["Element Code", "source_dataset"], "hash_fk_csv_column_name": "Element Code_id", "hash_fk_sql_column_name": "element_code_id", "hash_pk_sql_column_name": "id", "index_hash": "9b156b86_elements", "model_name": "Elements", "pipeline_name": "elements", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "element", "reference_pk_csv_column": "Element Code", "sql_column_name": "element_code", "table_name": "elements", "validation_func": "is_valid_element_code"}, {"csv_column_name": "Flag", "exception_func": "invalid_flag", "format_methods": ["upper"], "hash_columns": ["Flag"], "hash_fk_csv_column_name": "Flag_id", "hash_fk_sql_column_name": "flag_id", "hash_pk_sql_column_name": "id", "index_hash": "9b974387_flags", "model_name": "Flags", "pipeline_name": "flags", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "description", "reference_pk_csv_column": "Flag", "sql_column_name": "flag", "table_name": "flags", "validation_func": "is_valid_flag"}]
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dataset-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        # Breakdown Variable Code
        df['Breakdown Variable Code'] = df['Breakdown Variable Code'].astype(str).str.strip().str.replace("'", "")
        # Breakdown Variable
        df['Breakdown Variable'] = df['Breakdown Variable'].astype(str).str.strip().str.replace("'", "")
        # Breadown by Sex of the Household Head Code
        df['Breadown by Sex of the Household Head Code'] = df['Breadown by Sex of the Household Head Code'].astype(str).str.strip().str.replace("'", "")
        # Breadown by Sex of the Household Head
        df['Breadown by Sex of the Household Head'] = df['Breadown by Sex of the Household Head'].astype(str).str.strip().str.replace("'", "")
        # Unit
        df['Unit'] = df['Unit'].astype(str).str.strip().str.replace("'", "")
        # Value
        df['Value'] = df['Value'].astype(str).str.strip().str.replace("'", "")
        df['Value'] = df['Value'].replace({'<0.1': 0.05, 'nan': None})
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        # Foreign key columns
        record['survey_code_id'] = row['survey_code_id']
        record['indicator_code_id'] = row['indicator_code_id']
        record['element_code_id'] = row['element_code_id']
        record['flag_id'] = row['flag_id']
        # Data columns
        record['breakdown_variable_code'] = row['Breakdown Variable Code']
        record['breakdown_variable'] = row['Breakdown Variable']
        record['breadown_by_sex_of_the_household_head_code'] = row['Breadown by Sex of the Household Head Code']
        record['breadown_by_sex_of_the_household_head'] = row['Breadown by Sex of the Household Head']
        record['unit'] = row['Unit']
        record['value'] = row['Value']
        return record


# Module-level functions for backwards compatibility
etl = IndicatorsFromHouseholdSurveysETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)