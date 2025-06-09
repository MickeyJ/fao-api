import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .currencies_model import Currencies


class CurrenciesETL(BaseLookupETL):
    """ETL pipeline for currencies reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/currencies.csv"),
            model_class=Currencies,
            table_name="currencies",
            hash_columns=["ISO Currency Code", "source_dataset"],
            pk_column="ISO Currency Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['ISO Currency Code'] = df['ISO Currency Code'].astype(str).str.strip().str.replace("'", "")
        df['Currency'] = df['Currency'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['iso_currency_code'] = row['ISO Currency Code']
        record['currency'] = row['Currency']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = CurrenciesETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)