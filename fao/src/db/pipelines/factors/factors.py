import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .factors_model import Factors


class FactorsETL(BaseLookupETL):
    """ETL pipeline for factors reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/factors.csv"),
            model_class=Factors,
            table_name="factors",
            hash_columns=["Factor Code", "source_dataset"],
            pk_column="Factor Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Factor Code'] = df['Factor Code'].astype(str).str.strip().str.replace("'", "")
        df['Factor'] = df['Factor'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['factor_code'] = row['Factor Code']
        record['factor'] = row['Factor']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = FactorsETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)