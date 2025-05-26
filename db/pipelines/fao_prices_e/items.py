import pandas as pd
from sqlalchemy.orm import Session

from db.constants.column_names import ITEM_CODE, ITEM_NAME, CPC_CODE

from db.database import run_with_session
from . import get_data_from, strip_quote
from db.models import Item


CSV = get_data_from("Prices_E_ItemCodes.csv")


def load():
    """Load and preview item data."""
    print(f"Loading: {CSV}")
    df = pd.read_csv(CSV, dtype=str)
    df.columns = df.columns.str.strip()  # Clean up whitespace

    print(df.shape)
    print(df.head(5))
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with missing or malformed data"""
    initial_count = len(df)

    # drop rows with missing codes
    df = df.dropna(subset=[ITEM_CODE, CPC_CODE])

    # remove single quote from cpc code
    df[CPC_CODE] = strip_quote(df, CPC_CODE)

    # ensure item code is an integer
    df[ITEM_CODE] = df[ITEM_CODE].astype(int)

    # ensure cpc code is string and not null
    df[CPC_CODE] = df[CPC_CODE].fillna("").astype(str).str.strip()

    # strip whitespace from name
    df[ITEM_NAME] = df[ITEM_NAME].astype(str).str.strip()

    final_count = len(df)
    print(f"Validated items: {initial_count} → {final_count} rows")

    return df


def insert(df: pd.DataFrame, session: Session):
    """Insert items into the database."""
    for _, row in df.iterrows():
        item = Item(
            fao_code=row[ITEM_CODE],
            cpc_code=row[CPC_CODE],
            name=row[ITEM_NAME],
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
