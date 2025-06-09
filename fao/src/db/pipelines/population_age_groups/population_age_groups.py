import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .population_age_groups_model import PopulationAgeGroups


class PopulationAgeGroupsETL(BaseLookupETL):
    """ETL pipeline for population_age_groups reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/population_age_groups.csv"),
            model_class=PopulationAgeGroups,
            table_name="population_age_groups",
            hash_columns=["Population Age Group Code", "source_dataset"],
            pk_column="Population Age Group Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Population Age Group Code'] = df['Population Age Group Code'].astype(str).str.strip().str.replace("'", "")
        df['Population Age Group'] = df['Population Age Group'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['population_age_group_code'] = row['Population Age Group Code']
        record['population_age_group'] = row['Population Age Group']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = PopulationAgeGroupsETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)