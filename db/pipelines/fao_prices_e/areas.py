import pandas as pd
from sqlalchemy.orm import Session

from db.constants.column_names import CONST

from db.database import run_with_session
from . import get_data_from, strip_quote
from db.models import Area


CSV_PATH = get_data_from("Prices_E_AreaCodes.csv")


def load():
    """Load and preview area data"""
    print(f"Loading: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH, dtype=str)
    df.columns = df.columns.str.strip()  # clean whitespace

    print(df.shape)
    print(df.head(5))
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with missing or malformed data"""
    initial_count = len(df)

    # drop rows with missing codes
    df = df.dropna(subset=[CONST.CSV.AREA_CODE, CONST.CSV.M49_CODE])

    # remove single quote from m49 code
    df[CONST.CSV.M49_CODE] = strip_quote(df, CONST.CSV.M49_CODE)

    # ensure area code is an integer
    df[CONST.CSV.AREA_CODE] = df[CONST.CSV.AREA_CODE].astype(int)

    # ensure m49 code is string and not null
    df[CONST.CSV.M49_CODE] = df[CONST.CSV.M49_CODE].fillna("").astype(str).str.strip()

    # strip whitespace from name
    df[CONST.CSV.AREA_NAME] = df[CONST.CSV.AREA_NAME].astype(str).str.strip()

    final_count = len(df)
    print(f"Validated areas: {initial_count} → {final_count} rows")

    return df


def insert(df: pd.DataFrame, session: Session):
    """Insert areas into the database."""
    for _, row in df.iterrows():
        area = Area(
            fao_code=row[CONST.CSV.AREA_CODE],
            m49_code=row[CONST.CSV.M49_CODE],
            name=row[CONST.CSV.AREA_NAME],
        )
        session.merge(area)
    session.commit()
    print(f"Inserted {len(df)} items into the database.")


def run(db):
    df = load()
    df = clean(df)
    insert(df, db)


if __name__ == "__main__":
    run_with_session(run)
