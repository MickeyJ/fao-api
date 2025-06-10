import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .surveys_model import Surveys


class SurveysETL(BaseLookupETL):
    """ETL pipeline for surveys reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/surveys.csv"),
            model_class=Surveys,
            table_name="surveys",
            hash_columns=["Survey Code", "source_dataset"],
            pk_column="Survey Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Survey Code'] = df['Survey Code'].astype(str).str.strip().str.replace("'", "")
        df['Survey'] = df['Survey'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['survey_code'] = row['Survey Code']
        record['survey'] = row['Survey']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = SurveysETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)