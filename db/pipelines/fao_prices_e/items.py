import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from db.constants.column_names import CONST
from db.utils import strip_quote, load_csv
from db.database import run_with_session
from . import get_csv_path_for
from db.models import Item


CSV_PATH = get_csv_path_for("Prices_E_ItemCodes.csv")

table_name = "items"


def load():
    return load_csv(CSV_PATH)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with missing or malformed data"""
    if df.empty:
        print(f"No {table_name} data to clean.")
        return df

    print(f"\nCleaning {table_name} data...")
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
    print(f"Validated {table_name}: {initial_count} → {final_count} rows")

    return df


def insert(df: pd.DataFrame, session: Session):
    """Insert into the database."""
    if df.empty:
        print(f"No {table_name} data to insert.")
        return

    print(f"\nPreparing bulk {table_name} insert...")

    try:
        # Ensure the Area table exists
        Item.__table__.create(bind=session.bind, checkfirst=True)

        records = []
        for _, row in df.iterrows():
            records.append(
                {
                    CONST.DB.FAO_CODE: row[CONST.CSV.ITEM_CODE],
                    CONST.DB.CPC_CODE: row[CONST.CSV.CPC_CODE],
                    CONST.DB.NAME: row[CONST.CSV.ITEM_NAME],
                }
            )

        # Batch insert with conflict handling
        stmt = pg_insert(Item).values(records)
        stmt = stmt.on_conflict_do_nothing(index_elements=[CONST.DB.FAO_CODE])

        session.execute(stmt)
        session.commit()
        print(f"Inserted {len(df)} {table_name} into the database.")
    except Exception as e:
        print(f"Error inserting {table_name}: {e}")
        session.rollback()


def run(db):
    df = load()
    df = clean(df)
    insert(df, db)


if __name__ == "__main__":
    run_with_session(run)
