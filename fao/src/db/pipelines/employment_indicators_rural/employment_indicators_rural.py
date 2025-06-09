import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseDatasetETL
from .employment_indicators_rural_model import EmploymentIndicatorsRural


class EmploymentIndicatorsRuralETL(BaseDatasetETL):
    """ETL pipeline for employment_indicators_rural dataset"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("Employment_Indicators_Rural_E_All_Data_(Normalized)/Employment_Indicators_Rural_E_All_Data_(Normalized).csv"),
            model_class=EmploymentIndicatorsRural,
            table_name="employment_indicators_rural",
            exclude_columns=["Area", "Area Code", "Area Code (M49)", "Element", "Element Code", "Flag", "Indicator", "Indicator Code", "Sex", "Sex Code", "Source", "Source Code"],
            foreign_keys=[{"csv_column_name": "Area Code", "format_methods": [], "hash_columns": ["Area Code", "source_dataset"], "hash_fk_csv_column_name": "Area Code_id", "hash_fk_sql_column_name": "area_code_id", "hash_pk_sql_column_name": "id", "index_hash": "15f63a67_area_codes", "model_name": "AreaCodes", "pipeline_name": "area_codes", "reference_additional_columns": ["area_code_m49"], "reference_column_count": 4, "reference_description_column": "area", "reference_pk_csv_column": "Area Code", "sql_column_name": "area_code", "table_name": "area_codes"}, {"csv_column_name": "Source Code", "format_methods": [], "hash_columns": ["Source Code", "source_dataset"], "hash_fk_csv_column_name": "Source Code_id", "hash_fk_sql_column_name": "source_code_id", "hash_pk_sql_column_name": "id", "index_hash": "5a313b49_sources", "model_name": "Sources", "pipeline_name": "sources", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "source", "reference_pk_csv_column": "Source Code", "sql_column_name": "source_code", "table_name": "sources"}, {"csv_column_name": "Indicator Code", "format_methods": [], "hash_columns": ["Indicator Code", "source_dataset"], "hash_fk_csv_column_name": "Indicator Code_id", "hash_fk_sql_column_name": "indicator_code_id", "hash_pk_sql_column_name": "id", "index_hash": "cd6fd7fe_indicators", "model_name": "Indicators", "pipeline_name": "indicators", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "indicator", "reference_pk_csv_column": "Indicator Code", "sql_column_name": "indicator_code", "table_name": "indicators"}, {"csv_column_name": "Sex Code", "format_methods": [], "hash_columns": ["Sex Code", "source_dataset"], "hash_fk_csv_column_name": "Sex Code_id", "hash_fk_sql_column_name": "sex_code_id", "hash_pk_sql_column_name": "id", "index_hash": "f920305e_sexs", "model_name": "Sexs", "pipeline_name": "sexs", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "sex", "reference_pk_csv_column": "Sex Code", "sql_column_name": "sex_code", "table_name": "sexs"}, {"csv_column_name": "Element Code", "format_methods": [], "hash_columns": ["Element Code", "source_dataset"], "hash_fk_csv_column_name": "Element Code_id", "hash_fk_sql_column_name": "element_code_id", "hash_pk_sql_column_name": "id", "index_hash": "6ddfe8fd_elements", "model_name": "Elements", "pipeline_name": "elements", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "element", "reference_pk_csv_column": "Element Code", "sql_column_name": "element_code", "table_name": "elements"}, {"csv_column_name": "Flag", "format_methods": ["upper"], "hash_columns": ["Flag"], "hash_fk_csv_column_name": "Flag_id", "hash_fk_sql_column_name": "flag_id", "hash_pk_sql_column_name": "id", "index_hash": "3169ee22_flags", "model_name": "Flags", "pipeline_name": "flags", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "description", "reference_pk_csv_column": "Flag", "sql_column_name": "flag", "table_name": "flags"}]
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
        # Note
        df['Note'] = df['Note'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        # Foreign key columns
        record['area_code_id'] = row['area_code_id']
        record['source_code_id'] = row['source_code_id']
        record['indicator_code_id'] = row['indicator_code_id']
        record['sex_code_id'] = row['sex_code_id']
        record['element_code_id'] = row['element_code_id']
        record['flag_id'] = row['flag_id']
        # Data columns
        record['year_code'] = row['Year Code']
        record['year'] = row['Year']
        record['unit'] = row['Unit']
        record['value'] = row['Value']
        record['note'] = row['Note']
        return record


# Module-level functions for backwards compatibility
etl = EmploymentIndicatorsRuralETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)