import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from db.constants.column_names import CONST
from db.utils import load_csv
from db.database import run_with_session
from db.models import Currency
from . import get_data_from


CSV_PATH = get_data_from("Exchange_rate_E_Currencys.csv")

table_name = "currencies"


def load():
    return load_csv(CSV_PATH)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with missing or malformed data"""
    if df.empty:
        print(f"No {table_name} data to clean.")
        return df

    print(f"\nCleaning {table_name} data...")
    initial_count = len(df)

    # strip whitespace
    df[CONST.CSV.CURRENCY] = df[CONST.CSV.CURRENCY].astype(str).str.strip()
    df[CONST.CSV.CURRENCY_CODE] = df[CONST.CSV.CURRENCY_CODE].astype(str).str.strip()

    final_count = len(df)
    print(f"Validated {table_name}: {initial_count} → {final_count} rows")

    return df


def insert(df: pd.DataFrame, session: Session):
    """Insert currencies into the database."""
    if df.empty:
        print(f"No {table_name} data to insert.")
        return

    print(f"\nPreparing bulk {table_name} insert...")

    try:
        # Ensure the Area table exists
        Currency.__table__.create(bind=session.bind, checkfirst=True)

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
        stmt = stmt.on_conflict_do_nothing(index_elements=[CONST.DB.CURRENCY_CODE])

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
