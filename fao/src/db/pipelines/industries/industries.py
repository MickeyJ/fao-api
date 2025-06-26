import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .industries_model import Industries


class IndustriesETL(BaseLookupETL):
    """ETL pipeline for industries reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/industries.csv"),
            model_class=Industries,
            table_name="industries",
            hash_columns=["Industry Code", "source_dataset"],
            pk_column="Industry Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Industry Code'] = df['Industry Code'].astype(str).str.strip().str.replace("'", "")
        df['Industry'] = df['Industry'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['industry_code'] = row['Industry Code']
        record['industry'] = row['Industry']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = IndustriesETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)