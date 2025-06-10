import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .geographic_levels_model import GeographicLevels


class GeographicLevelsETL(BaseLookupETL):
    """ETL pipeline for geographic_levels reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/geographic_levels.csv"),
            model_class=GeographicLevels,
            table_name="geographic_levels",
            hash_columns=["Geographic Level Code", "source_dataset"],
            pk_column="Geographic Level Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Geographic Level Code'] = df['Geographic Level Code'].astype(str).str.strip().str.replace("'", "")
        df['Geographic Level'] = df['Geographic Level'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['geographic_level_code'] = row['Geographic Level Code']
        record['geographic_level'] = row['Geographic Level']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = GeographicLevelsETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)