import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db.constants.column_names import CONST

from db.database import run_with_session
from . import get_data_from, strip_quote
from db.models import Currency


CSV_PATH = get_data_from("Exchange_rate_E_Currencys.csv")


def load():
    """Load and preview item data."""
    print(f"Loading: {CSV_PATH}")
    try:
        df = pd.read_csv(CSV_PATH, dtype=str)
    except FileNotFoundError:
        print(f"File not found: {CSV_PATH}")
        return pd.DataFrame()

    df.columns = df.columns.str.strip()  # Clean up column name whitespace

    print(df.shape)
    print(df.head(5))
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with missing or malformed data"""
    if df.empty:
        print("No currency data to clean.")
        return df

    initial_count = len(df)

    # strip whitespace
    df[CONST.CSV.CURRENCY] = df[CONST.CSV.CURRENCY].astype(str).str.strip()
    df[CONST.CSV.CURRENCY_CODE] = df[CONST.CSV.CURRENCY_CODE].astype(str).str.strip()

    final_count = len(df)
    print(f"Validated items: {initial_count} → {final_count} rows")

    return df


def insert(df: pd.DataFrame, session: Session):
    """Insert currencies into the database."""
    if df.empty:
        print("No currency data to insert.")
        return
    records = []
    for _, row in df.iterrows():
        records.append(
            {
                CONST.DB.CURRENCY_NAME: row[CONST.CSV.CURRENCY],
                CONST.DB.CURRENCY_CODE: row[CONST.CSV.CURRENCY_CODE],
            }
        )

    # Batch insert with conflict handling
    stmt = pg_insert(Currency).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=[CONST.DB.CURRENCY_CODE],
        set_={CONST.DB.CURRENCY_NAME: stmt.excluded.currency_name},
    )

    session.execute(stmt)
    session.commit()
    print(f"Inserted {len(df)} currencies into the database.")


def run(db):
    df = load()
    df = clean(df)
    insert(df, db)


if __name__ == "__main__":
    run_with_session(run)
