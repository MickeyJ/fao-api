import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .area_codes_model import AreaCodes


class AreaCodesETL(BaseLookupETL):
    """ETL pipeline for area_codes reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/area_codes.csv"),
            model_class=AreaCodes,
            table_name="area_codes",
            hash_columns=["Area Code", "source_dataset"],
            pk_column="Area Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Area Code'] = df['Area Code'].astype(str).str.strip().str.replace("'", "")
        df['Area'] = df['Area'].astype(str).str.strip().str.replace("'", "")
        df['Area Code (M49)'] = df['Area Code (M49)'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['area_code'] = row['Area Code']
        record['area'] = row['Area']
        record['area_code_m49'] = row['Area Code (M49)']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = AreaCodesETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)