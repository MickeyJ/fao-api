import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseDatasetETL
from .value_shares_industry_primary_factors_model import ValueSharesIndustryPrimaryFactors


class ValueSharesIndustryPrimaryFactorsETL(BaseDatasetETL):
    """ETL pipeline for value_shares_industry_primary_factors dataset"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("Value_shares_industry_primary_factors_E_All_Data_(Normalized)/Value_shares_industry_primary_factors_E_All_Data_(Normalized).csv"),
            model_class=ValueSharesIndustryPrimaryFactors,
            table_name="value_shares_industry_primary_factors",
            exclude_columns=["Area", "Area Code", "Area Code (M49)", "Element", "Element Code", "Flag"],
            foreign_keys=[{"csv_column_name": "Area Code", "exception_func": "invalid_area_code", "format_methods": [], "hash_columns": ["Area Code", "source_dataset"], "hash_fk_csv_column_name": "Area Code_id", "hash_fk_sql_column_name": "area_code_id", "hash_pk_sql_column_name": "id", "index_hash": "2b9877fb_area_codes", "model_name": "AreaCodes", "pipeline_name": "area_codes", "reference_additional_columns": ["area_code_m49"], "reference_column_count": 4, "reference_description_column": "area", "reference_pk_csv_column": "Area Code", "sql_column_name": "area_code", "table_name": "area_codes", "validation_func": "is_valid_area_code"}, {"csv_column_name": "Element Code", "exception_func": "invalid_element_code", "format_methods": [], "hash_columns": ["Element Code", "source_dataset"], "hash_fk_csv_column_name": "Element Code_id", "hash_fk_sql_column_name": "element_code_id", "hash_pk_sql_column_name": "id", "index_hash": "8f579a71_elements", "model_name": "Elements", "pipeline_name": "elements", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "element", "reference_pk_csv_column": "Element Code", "sql_column_name": "element_code", "table_name": "elements", "validation_func": "is_valid_element_code"}, {"csv_column_name": "Flag", "exception_func": "invalid_flag", "format_methods": ["upper"], "hash_columns": ["Flag"], "hash_fk_csv_column_name": "Flag_id", "hash_fk_sql_column_name": "flag_id", "hash_pk_sql_column_name": "id", "index_hash": "46cf6cfc_flags", "model_name": "Flags", "pipeline_name": "flags", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "description", "reference_pk_csv_column": "Flag", "sql_column_name": "flag", "table_name": "flags", "validation_func": "is_valid_flag"}]
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dataset-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        # Food Value Code
        df['Food Value Code'] = df['Food Value Code'].astype(str).str.strip().str.replace("'", "")
        # Food Value
        df['Food Value'] = df['Food Value'].astype(str).str.strip().str.replace("'", "")
        # Industry Code
        df['Industry Code'] = df['Industry Code'].astype(str).str.strip().str.replace("'", "")
        # Industry
        df['Industry'] = df['Industry'].astype(str).str.strip().str.replace("'", "")
        # Factor Code
        df['Factor Code'] = df['Factor Code'].astype(str).str.strip().str.replace("'", "")
        # Factor
        df['Factor'] = df['Factor'].astype(str).str.strip().str.replace("'", "")
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
        record['element_code_id'] = row['element_code_id']
        record['flag_id'] = row['flag_id']
        # Data columns
        record['food_value_code'] = row['Food Value Code']
        record['food_value'] = row['Food Value']
        record['industry_code'] = row['Industry Code']
        record['industry'] = row['Industry']
        record['factor_code'] = row['Factor Code']
        record['factor'] = row['Factor']
        record['year_code'] = row['Year Code']
        record['year'] = row['Year']
        record['unit'] = row['Unit']
        record['value'] = row['Value']
        return record


# Module-level functions for backwards compatibility
etl = ValueSharesIndustryPrimaryFactorsETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)