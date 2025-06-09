import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .indicators_model import Indicators


class IndicatorsETL(BaseLookupETL):
    """ETL pipeline for indicators reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/indicators.csv"),
            model_class=Indicators,
            table_name="indicators",
            hash_columns=["Indicator Code", "source_dataset"],
            pk_column="Indicator Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Indicator Code'] = df['Indicator Code'].astype(str).str.strip().str.replace("'", "")
        df['Indicator'] = df['Indicator'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['indicator_code'] = row['Indicator Code']
        record['indicator'] = row['Indicator']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = IndicatorsETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)