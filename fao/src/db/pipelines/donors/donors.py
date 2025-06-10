import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .donors_model import Donors


class DonorsETL(BaseLookupETL):
    """ETL pipeline for donors reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/donors.csv"),
            model_class=Donors,
            table_name="donors",
            hash_columns=["Donor Code", "source_dataset"],
            pk_column="Donor Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Donor Code'] = df['Donor Code'].astype(str).str.strip().str.replace("'", "")
        df['Donor'] = df['Donor'].astype(str).str.strip().str.replace("'", "")
        df['Donor Code (M49)'] = df['Donor Code (M49)'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['donor_code'] = row['Donor Code']
        record['donor'] = row['Donor']
        record['donor_code_m49'] = row['Donor Code (M49)']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = DonorsETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)