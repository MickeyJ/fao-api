import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .partner_country_codes_model import PartnerCountryCodes


class PartnerCountryCodesETL(BaseLookupETL):
    """ETL pipeline for partner_country_codes reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/partner_country_codes.csv"),
            model_class=PartnerCountryCodes,
            table_name="partner_country_codes",
            hash_columns=["Partner Country Code", "source_dataset"],
            pk_column="Partner Country Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Partner Country Code'] = df['Partner Country Code'].astype(str).str.strip().str.replace("'", "")
        df['Partner Countries'] = df['Partner Countries'].astype(str).str.strip().str.replace("'", "")
        df['Partner Country Code (M49)'] = df['Partner Country Code (M49)'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['partner_country_code'] = row['Partner Country Code']
        record['partner_countries'] = row['Partner Countries']
        record['partner_country_code_m49'] = row['Partner Country Code (M49)']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = PartnerCountryCodesETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)