import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseDatasetETL
from .minimum_dietary_diversity_for_women_mdd_w_food_and_diet_model import MinimumDietaryDiversityForWomenMddWFoodAndDiet


class MinimumDietaryDiversityForWomenMddWFoodAndDietETL(BaseDatasetETL):
    """ETL pipeline for minimum_dietary_diversity_for_women_mdd_w_food_and_diet dataset"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("Minimum_Dietary_Diversity_for_Women_(MDD-W)_Food_and_Diet_E_All_Data_(Normalized)/Minimum_Dietary_Diversity_for_Women_(MDD-W)_Food_and_Diet_E_All_Data_(Normalized).csv"),
            model_class=MinimumDietaryDiversityForWomenMddWFoodAndDiet,
            table_name="minimum_dietary_diversity_for_women_mdd_w_food_and_diet",
            exclude_columns=["Element", "Element Code", "Flag", "Food Group", "Food Group Code", "Geographic Level", "Geographic Level Code", "Indicator", "Indicator Code", "Survey", "Survey Code"],
            foreign_keys=[{"csv_column_name": "Survey Code", "format_methods": [], "hash_columns": ["Survey Code", "source_dataset"], "hash_fk_csv_column_name": "Survey Code_id", "hash_fk_sql_column_name": "survey_code_id", "hash_pk_sql_column_name": "id", "index_hash": "5496720a_surveys", "model_name": "Surveys", "pipeline_name": "surveys", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "survey", "reference_pk_csv_column": "Survey Code", "sql_column_name": "survey_code", "table_name": "surveys"}, {"csv_column_name": "Food Group Code", "format_methods": [], "hash_columns": ["Food Group Code", "source_dataset"], "hash_fk_csv_column_name": "Food Group Code_id", "hash_fk_sql_column_name": "food_group_code_id", "hash_pk_sql_column_name": "id", "index_hash": "d19b4f5a_food_groups", "model_name": "FoodGroups", "pipeline_name": "food_groups", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "food_group", "reference_pk_csv_column": "Food Group Code", "sql_column_name": "food_group_code", "table_name": "food_groups"}, {"csv_column_name": "Indicator Code", "format_methods": [], "hash_columns": ["Indicator Code", "source_dataset"], "hash_fk_csv_column_name": "Indicator Code_id", "hash_fk_sql_column_name": "indicator_code_id", "hash_pk_sql_column_name": "id", "index_hash": "c15e729f_indicators", "model_name": "Indicators", "pipeline_name": "indicators", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "indicator", "reference_pk_csv_column": "Indicator Code", "sql_column_name": "indicator_code", "table_name": "indicators"}, {"csv_column_name": "Geographic Level Code", "format_methods": [], "hash_columns": ["Geographic Level Code", "source_dataset"], "hash_fk_csv_column_name": "Geographic Level Code_id", "hash_fk_sql_column_name": "geographic_level_code_id", "hash_pk_sql_column_name": "id", "index_hash": "3e1550c5_geographic_levels", "model_name": "GeographicLevels", "pipeline_name": "geographic_levels", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "geographic_level", "reference_pk_csv_column": "Geographic Level Code", "sql_column_name": "geographic_level_code", "table_name": "geographic_levels"}, {"csv_column_name": "Element Code", "format_methods": [], "hash_columns": ["Element Code", "source_dataset"], "hash_fk_csv_column_name": "Element Code_id", "hash_fk_sql_column_name": "element_code_id", "hash_pk_sql_column_name": "id", "index_hash": "1500fef2_elements", "model_name": "Elements", "pipeline_name": "elements", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "element", "reference_pk_csv_column": "Element Code", "sql_column_name": "element_code", "table_name": "elements"}, {"csv_column_name": "Flag", "format_methods": ["upper"], "hash_columns": ["Flag"], "hash_fk_csv_column_name": "Flag_id", "hash_fk_sql_column_name": "flag_id", "hash_pk_sql_column_name": "id", "index_hash": "71c829d5_flags", "model_name": "Flags", "pipeline_name": "flags", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "description", "reference_pk_csv_column": "Flag", "sql_column_name": "flag", "table_name": "flags"}]
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
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        # Foreign key columns
        record['survey_code_id'] = row['survey_code_id']
        record['food_group_code_id'] = row['food_group_code_id']
        record['indicator_code_id'] = row['indicator_code_id']
        record['geographic_level_code_id'] = row['geographic_level_code_id']
        record['element_code_id'] = row['element_code_id']
        record['flag_id'] = row['flag_id']
        # Data columns
        record['unit'] = row['Unit']
        record['value'] = row['Value']
        return record


# Module-level functions for backwards compatibility
etl = MinimumDietaryDiversityForWomenMddWFoodAndDietETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)