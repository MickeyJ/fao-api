import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseDatasetETL
from .cost_affordability_healthy_diet_co_ahd_model import CostAffordabilityHealthyDietCoAhd


class CostAffordabilityHealthyDietCoAhdETL(BaseDatasetETL):
    """ETL pipeline for cost_affordability_healthy_diet_co_ahd dataset"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("Cost_Affordability_Healthy_Diet_(CoAHD)_E_All_Data_(Normalized)/Cost_Affordability_Healthy_Diet_(CoAHD)_E_All_Data_(Normalized).csv"),
            model_class=CostAffordabilityHealthyDietCoAhd,
            table_name="cost_affordability_healthy_diet_co_ahd",
            exclude_columns=["Area", "Area Code", "Area Code (M49)", "Element", "Element Code", "Flag", "Item", "Item Code", "Release", "Release Code"],
            foreign_keys=[{"csv_column_name": "Area Code", "format_methods": [], "hash_columns": ["Area Code", "source_dataset"], "hash_fk_csv_column_name": "Area Code_id", "hash_fk_sql_column_name": "area_code_id", "hash_pk_sql_column_name": "id", "index_hash": "270c97a6_area_codes", "model_name": "AreaCodes", "pipeline_name": "area_codes", "reference_additional_columns": ["area_code_m49"], "reference_column_count": 4, "reference_description_column": "area", "reference_pk_csv_column": "Area Code", "sql_column_name": "area_code", "table_name": "area_codes"}, {"csv_column_name": "Item Code", "format_methods": [], "hash_columns": ["Item Code", "source_dataset"], "hash_fk_csv_column_name": "Item Code_id", "hash_fk_sql_column_name": "item_code_id", "hash_pk_sql_column_name": "id", "index_hash": "ceae5156_item_codes", "model_name": "ItemCodes", "pipeline_name": "item_codes", "reference_additional_columns": ["item_code_cpc", "item_code_fbs", "item_code_sdg"], "reference_column_count": 6, "reference_description_column": "item", "reference_pk_csv_column": "Item Code", "sql_column_name": "item_code", "table_name": "item_codes"}, {"csv_column_name": "Element Code", "format_methods": [], "hash_columns": ["Element Code", "source_dataset"], "hash_fk_csv_column_name": "Element Code_id", "hash_fk_sql_column_name": "element_code_id", "hash_pk_sql_column_name": "id", "index_hash": "698c6c34_elements", "model_name": "Elements", "pipeline_name": "elements", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "element", "reference_pk_csv_column": "Element Code", "sql_column_name": "element_code", "table_name": "elements"}, {"csv_column_name": "Release Code", "format_methods": [], "hash_columns": ["Release Code", "source_dataset"], "hash_fk_csv_column_name": "Release Code_id", "hash_fk_sql_column_name": "release_code_id", "hash_pk_sql_column_name": "id", "index_hash": "4f69315b_releases", "model_name": "Releases", "pipeline_name": "releases", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "release", "reference_pk_csv_column": "Release Code", "sql_column_name": "release_code", "table_name": "releases"}, {"csv_column_name": "Flag", "format_methods": ["upper"], "hash_columns": ["Flag"], "hash_fk_csv_column_name": "Flag_id", "hash_fk_sql_column_name": "flag_id", "hash_pk_sql_column_name": "id", "index_hash": "ec41bea5_flags", "model_name": "Flags", "pipeline_name": "flags", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "description", "reference_pk_csv_column": "Flag", "sql_column_name": "flag", "table_name": "flags"}]
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dataset-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        # Year Code
        df['Year Code'] = df['Year Code'].astype(str).str.strip().str.replace("'", "")
        # Year
        df['Year'] = df['Year'].astype(str).str.strip().str.replace("'", "")
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
        record['area_code_id'] = row['area_code_id']
        record['item_code_id'] = row['item_code_id']
        record['element_code_id'] = row['element_code_id']
        record['release_code_id'] = row['release_code_id']
        record['flag_id'] = row['flag_id']
        # Data columns
        record['year_code'] = row['Year Code']
        record['year'] = row['Year']
        record['unit'] = row['Unit']
        record['value'] = row['Value']
        return record


# Module-level functions for backwards compatibility
etl = CostAffordabilityHealthyDietCoAhdETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)