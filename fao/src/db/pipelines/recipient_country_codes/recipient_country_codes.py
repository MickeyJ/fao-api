import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .recipient_country_codes_model import RecipientCountryCodes


class RecipientCountryCodesETL(BaseLookupETL):
    """ETL pipeline for recipient_country_codes reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/recipient_country_codes.csv"),
            model_class=RecipientCountryCodes,
            table_name="recipient_country_codes",
            hash_columns=["Recipient Country Code", "source_dataset"],
            pk_column="Recipient Country Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Recipient Country Code'] = df['Recipient Country Code'].astype(str).str.strip().str.replace("'", "")
        df['Recipient Country'] = df['Recipient Country'].astype(str).str.strip().str.replace("'", "")
        df['Recipient Country Code (M49)'] = df['Recipient Country Code (M49)'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['recipient_country_code'] = row['Recipient Country Code']
        record['recipient_country'] = row['Recipient Country']
        record['recipient_country_code_m49'] = row['Recipient Country Code (M49)']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = RecipientCountryCodesETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)