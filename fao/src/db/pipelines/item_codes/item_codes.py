import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .item_codes_model import ItemCodes


class ItemCodesETL(BaseLookupETL):
    """ETL pipeline for item_codes reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/item_codes.csv"),
            model_class=ItemCodes,
            table_name="item_codes",
            hash_columns=["Item Code", "source_dataset"],
            pk_column="Item Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Item Code'] = df['Item Code'].astype(str).str.strip().str.replace("'", "")
        df['Item'] = df['Item'].astype(str).str.strip().str.replace("'", "")
        df['Item Code (CPC)'] = df['Item Code (CPC)'].astype(str).str.strip().str.replace("'", "")
        df['Item Code (FBS)'] = df['Item Code (FBS)'].astype(str).str.strip().str.replace("'", "")
        df['Item Code (SDG)'] = df['Item Code (SDG)'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['item_code'] = row['Item Code']
        record['item'] = row['Item']
        record['item_code_cpc'] = row['Item Code (CPC)']
        record['item_code_fbs'] = row['Item Code (FBS)']
        record['item_code_sdg'] = row['Item Code (SDG)']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = ItemCodesETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)