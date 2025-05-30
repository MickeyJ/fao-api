import pandas as pd
from sqlalchemy.orm import Session

from db.constants.column_names import CONST

from db.database import run_with_session
from . import get_data_from, strip_quote
from db.models import Item


CSV_PATH = get_data_from("Prices_E_ItemCodes.csv")


def load():
    """Load and preview item data."""
    print(f"Loading: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH, dtype=str)
    df.columns = df.columns.str.strip()  # Clean up whitespace

    print(df.shape)
    print(df.head(5))
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with missing or malformed data"""
    initial_count = len(df)

    # drop rows with missing codes
    df = df.dropna(subset=[CONST.CSV.ITEM_CODE, CONST.CSV.CPC_CODE])

    # remove single quote from cpc code
    df[CONST.CSV.CPC_CODE] = strip_quote(df, CONST.CSV.CPC_CODE)

    # ensure item code is an integer
    df[CONST.CSV.ITEM_CODE] = df[CONST.CSV.ITEM_CODE].astype(int)

    # ensure cpc code is string and not null
    df[CONST.CSV.CPC_CODE] = df[CONST.CSV.CPC_CODE].fillna("").astype(str).str.strip()

    # strip whitespace from name
    df[CONST.CSV.ITEM_NAME] = df[CONST.CSV.ITEM_NAME].astype(str).str.strip()

    final_count = len(df)
    print(f"Validated items: {initial_count} → {final_count} rows")

    return df


def insert(df: pd.DataFrame, session: Session):
    """Insert items into the database."""
    for _, row in df.iterrows():
        item = Item(
            fao_code=row[CONST.CSV.ITEM_CODE],
            cpc_code=row[CONST.CSV.CPC_CODE],
            name=row[CONST.CSV.ITEM_NAME],
        )
        session.merge(item)
    session.commit()
    print(f"Inserted {len(df)} items into the database.")


def run(db):
    df = load()
    df = clean(df)
    insert(df, db)


if __name__ == "__main__":
    run_with_session(run)
