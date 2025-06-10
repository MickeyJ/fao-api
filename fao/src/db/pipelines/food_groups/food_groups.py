import pandas as pd
from fao.src.db.utils import get_csv_path_for
from fao.src.db.database import run_with_session
from fao.src.db.pipelines.base import BaseLookupETL
from .food_groups_model import FoodGroups


class FoodGroupsETL(BaseLookupETL):
    """ETL pipeline for food_groups reference data"""
    
    def __init__(self):
        super().__init__(
            csv_path=get_csv_path_for("synthetic_references/food_groups.csv"),
            model_class=FoodGroups,
            table_name="food_groups",
            hash_columns=["Food Group Code", "source_dataset"],
            pk_column="Food Group Code"
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reference-specific cleaning"""
        # Common cleaning first
        df = self.base_clean(df)
        
        # Column-specific cleaning
        df['Food Group Code'] = df['Food Group Code'].astype(str).str.strip().str.replace("'", "")
        df['Food Group'] = df['Food Group'].astype(str).str.strip().str.replace("'", "")
        df['source_dataset'] = df['source_dataset'].astype(str).str.strip().str.replace("'", "")
        
        return df
    
    def build_record(self, row: pd.Series) -> dict:
        """Build record for insertion"""
        record = {}
        record['food_group_code'] = row['Food Group Code']
        record['food_group'] = row['Food Group']
        record['source_dataset'] = row['source_dataset']
        return record


# Module-level functions for backwards compatibility
etl = FoodGroupsETL()
load = etl.load
clean = etl.clean
insert = etl.insert
run = etl.run

if __name__ == "__main__":
    run_with_session(run)