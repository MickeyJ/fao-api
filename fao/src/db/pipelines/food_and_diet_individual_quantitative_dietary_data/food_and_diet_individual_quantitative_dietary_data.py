import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseDatasetETL
from .food_and_diet_individual_quantitative_dietary_data_model import FoodAndDietIndividualQuantitativeDietaryData


class FoodAndDietIndividualQuantitativeDietaryDataETL(BaseDatasetETL):
    """ETL pipeline for food_and_diet_individual_quantitative_dietary_data dataset"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("Food_and_Diet_Individual_Quantitative_Dietary_Data_E_All_Data_(Normalized)/Food_and_Diet_Individual_Quantitative_Dietary_Data_E_All_Data_(Normalized).csv"),
            model_class=FoodAndDietIndividualQuantitativeDietaryData,
            table_name="food_and_diet_individual_quantitative_dietary_data",
            column_renames={"Population Group Code": "Population Age Group Code"},
            exclude_columns=["Element", "Element Code", "Flag", "Food Group", "Food Group Code", "Geographic Level", "Geographic Level Code", "Indicator", "Indicator Code", "Population Group", "Sex", "Sex Code", "Survey", "Survey Code"],
            foreign_keys=[{"csv_column_name": "Survey Code", "format_methods": [], "hash_columns": ["Survey Code", "source_dataset"], "hash_fk_csv_column_name": "Survey Code_id", "hash_fk_sql_column_name": "survey_code_id", "hash_pk_sql_column_name": "id", "index_hash": "8992a999_surveys", "model_name": "Surveys", "pipeline_name": "surveys", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "survey", "reference_pk_csv_column": "Survey Code", "sql_column_name": "survey_code", "table_name": "surveys"}, {"csv_column_name": "Geographic Level Code", "format_methods": [], "hash_columns": ["Geographic Level Code", "source_dataset"], "hash_fk_csv_column_name": "Geographic Level Code_id", "hash_fk_sql_column_name": "geographic_level_code_id", "hash_pk_sql_column_name": "id", "index_hash": "03d950cb_geographic_levels", "model_name": "GeographicLevels", "pipeline_name": "geographic_levels", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "geographic_level", "reference_pk_csv_column": "Geographic Level Code", "sql_column_name": "geographic_level_code", "table_name": "geographic_levels"}, {"csv_column_name": "Population Group Code", "format_methods": [], "hash_columns": ["Population Age Group Code", "source_dataset"], "hash_fk_csv_column_name": "Population Group Code_id", "hash_fk_sql_column_name": "population_age_group_code_id", "hash_pk_sql_column_name": "id", "index_hash": "fa79ae92_population_age_groups", "model_name": "PopulationAgeGroups", "pipeline_name": "population_age_groups", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "population_age_group", "reference_pk_csv_column": "Population Age Group Code", "sql_column_name": "population_age_group_code", "table_name": "population_age_groups"}, {"csv_column_name": "Food Group Code", "format_methods": [], "hash_columns": ["Food Group Code", "source_dataset"], "hash_fk_csv_column_name": "Food Group Code_id", "hash_fk_sql_column_name": "food_group_code_id", "hash_pk_sql_column_name": "id", "index_hash": "290e822d_food_groups", "model_name": "FoodGroups", "pipeline_name": "food_groups", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "food_group", "reference_pk_csv_column": "Food Group Code", "sql_column_name": "food_group_code", "table_name": "food_groups"}, {"csv_column_name": "Indicator Code", "format_methods": [], "hash_columns": ["Indicator Code", "source_dataset"], "hash_fk_csv_column_name": "Indicator Code_id", "hash_fk_sql_column_name": "indicator_code_id", "hash_pk_sql_column_name": "id", "index_hash": "24ef83e0_indicators", "model_name": "Indicators", "pipeline_name": "indicators", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "indicator", "reference_pk_csv_column": "Indicator Code", "sql_column_name": "indicator_code", "table_name": "indicators"}, {"csv_column_name": "Element Code", "format_methods": [], "hash_columns": ["Element Code", "source_dataset"], "hash_fk_csv_column_name": "Element Code_id", "hash_fk_sql_column_name": "element_code_id", "hash_pk_sql_column_name": "id", "index_hash": "9efb55f3_elements", "model_name": "Elements", "pipeline_name": "elements", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "element", "reference_pk_csv_column": "Element Code", "sql_column_name": "element_code", "table_name": "elements"}, {"csv_column_name": "Sex Code", "format_methods": [], "hash_columns": ["Sex Code", "source_dataset"], "hash_fk_csv_column_name": "Sex Code_id", "hash_fk_sql_column_name": "sex_code_id", "hash_pk_sql_column_name": "id", "index_hash": "30c03653_sexs", "model_name": "Sexs", "pipeline_name": "sexs", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "sex", "reference_pk_csv_column": "Sex Code", "sql_column_name": "sex_code", "table_name": "sexs"}, {"csv_column_name": "Flag", "format_methods": ["upper"], "hash_columns": ["Flag"], "hash_fk_csv_column_name": "Flag_id", "hash_fk_sql_column_name": "flag_id", "hash_pk_sql_column_name": "id", "index_hash": "6dfdfc92_flags", "model_name": "Flags", "pipeline_name": "flags", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "description", "reference_pk_csv_column": "Flag", "sql_column_name": "flag", "table_name": "flags"}]
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dataset-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        # Population Age Group Code
        df['Population Age Group Code'] = df['Population Age Group Code'].astype(str).str.strip().str.replace("'", "")
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
        record['population_age_group_code_id'] = row['population_age_group_code_id']
        record['food_group_code_id'] = row['food_group_code_id']
        record['indicator_code_id'] = row['indicator_code_id']
        record['element_code_id'] = row['element_code_id']
        record['sex_code_id'] = row['sex_code_id']
        record['flag_id'] = row['flag_id']
        # Data columns
        record['population_age_group_code'] = row['Population Age Group Code']
        record['unit'] = row['Unit']
        record['value'] = row['Value']
        record['note'] = row['Note']
        return record


# Module-level functions for backwards compatibility
etl = FoodAndDietIndividualQuantitativeDietaryDataETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)