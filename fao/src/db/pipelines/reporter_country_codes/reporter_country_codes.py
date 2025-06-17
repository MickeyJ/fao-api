import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .reporter_country_codes_model import ReporterCountryCodes


class ReporterCountryCodesETL(BaseLookupETL):
    """ETL pipeline for reporter_country_codes reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/reporter_country_codes.csv"),
            model_class=ReporterCountryCodes,
            table_name="reporter_country_codes",
            hash_columns=["Reporter Country Code", "source_dataset"],
            pk_column="Reporter Country Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Reporter Country Code'] = df['Reporter Country Code'].astype(str).str.strip().str.replace("'", "")
        df['Reporter Countries'] = df['Reporter Countries'].astype(str).str.strip().str.replace("'", "")
        df['Reporter Country Code (M49)'] = df['Reporter Country Code (M49)'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['reporter_country_code'] = row['Reporter Country Code']
        record['reporter_countries'] = row['Reporter Countries']
        record['reporter_country_code_m49'] = row['Reporter Country Code (M49)']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = ReporterCountryCodesETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)