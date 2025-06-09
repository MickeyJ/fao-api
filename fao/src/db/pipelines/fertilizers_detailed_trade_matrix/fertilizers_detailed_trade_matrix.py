import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseDatasetETL
from .fertilizers_detailed_trade_matrix_model import FertilizersDetailedTradeMatrix


class FertilizersDetailedTradeMatrixETL(BaseDatasetETL):
    """ETL pipeline for fertilizers_detailed_trade_matrix dataset"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("Fertilizers_DetailedTradeMatrix_E_All_Data_(Normalized)/Fertilizers_DetailedTradeMatrix_E_All_Data_(Normalized).csv"),
            model_class=FertilizersDetailedTradeMatrix,
            table_name="fertilizers_detailed_trade_matrix",
            exclude_columns=["Element", "Element Code", "Flag", "Item", "Item Code", "Item Code (CPC)"],
            foreign_keys=[{"csv_column_name": "Item Code", "format_methods": [], "hash_columns": ["Item Code", "source_dataset"], "hash_fk_csv_column_name": "Item Code_id", "hash_fk_sql_column_name": "item_code_id", "hash_pk_sql_column_name": "id", "index_hash": "589c799c_item_codes", "model_name": "ItemCodes", "pipeline_name": "item_codes", "reference_additional_columns": ["item_code_cpc", "item_code_fbs", "item_code_sdg"], "reference_column_count": 6, "reference_description_column": "item", "reference_pk_csv_column": "Item Code", "sql_column_name": "item_code", "table_name": "item_codes"}, {"csv_column_name": "Element Code", "format_methods": [], "hash_columns": ["Element Code", "source_dataset"], "hash_fk_csv_column_name": "Element Code_id", "hash_fk_sql_column_name": "element_code_id", "hash_pk_sql_column_name": "id", "index_hash": "f301cc79_elements", "model_name": "Elements", "pipeline_name": "elements", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "element", "reference_pk_csv_column": "Element Code", "sql_column_name": "element_code", "table_name": "elements"}, {"csv_column_name": "Flag", "format_methods": ["upper"], "hash_columns": ["Flag"], "hash_fk_csv_column_name": "Flag_id", "hash_fk_sql_column_name": "flag_id", "hash_pk_sql_column_name": "id", "index_hash": "01c85306_flags", "model_name": "Flags", "pipeline_name": "flags", "reference_additional_columns": [], "reference_column_count": 3, "reference_description_column": "description", "reference_pk_csv_column": "Flag", "sql_column_name": "flag", "table_name": "flags"}]
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dataset-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        # Reporter Country Code
        df['Reporter Country Code'] = df['Reporter Country Code'].astype(str).str.strip().str.replace("'", "")
        # Reporter Country Code (M49)
        df['Reporter Country Code (M49)'] = df['Reporter Country Code (M49)'].astype(str).str.strip().str.replace("'", "")
        # Reporter Countries
        df['Reporter Countries'] = df['Reporter Countries'].astype(str).str.strip().str.replace("'", "")
        # Partner Country Code
        df['Partner Country Code'] = df['Partner Country Code'].astype(str).str.strip().str.replace("'", "")
        # Partner Country Code (M49)
        df['Partner Country Code (M49)'] = df['Partner Country Code (M49)'].astype(str).str.strip().str.replace("'", "")
        # Partner Countries
        df['Partner Countries'] = df['Partner Countries'].astype(str).str.strip().str.replace("'", "")
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
        record['item_code_id'] = row['item_code_id']
        record['element_code_id'] = row['element_code_id']
        record['flag_id'] = row['flag_id']
        # Data columns
        record['reporter_country_code'] = row['Reporter Country Code']
        record['reporter_country_code_m49'] = row['Reporter Country Code (M49)']
        record['reporter_countries'] = row['Reporter Countries']
        record['partner_country_code'] = row['Partner Country Code']
        record['partner_country_code_m49'] = row['Partner Country Code (M49)']
        record['partner_countries'] = row['Partner Countries']
        record['year_code'] = row['Year Code']
        record['year'] = row['Year']
        record['unit'] = row['Unit']
        record['value'] = row['Value']
        return record


# Module-level functions for backwards compatibility
etl = FertilizersDetailedTradeMatrixETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)