import pandas as pd
from pathlib import Path

from app.database import SessionLocal

DATA_DIR = "https://food-oasis-data.s3.amazonaws.com/Prices_E_All_Data_(Normalized)"
# DATA_DIR = Path(r"C:\Users\18057\Documents\Data\Food_FAO\Organized\Prices_E_All_Data_(Normalized)")


def strip_quote(df: pd.DataFrame, column_name):
    return df[column_name].str.replace("'", "").str.strip()


def get_data_from(filename):
    return f"{DATA_DIR}/{filename}"


def run_with_session(fn):
    session = SessionLocal()
    try:
        fn(session)
    finally:
        session.close()
