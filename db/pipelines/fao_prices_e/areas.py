import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from db.constants.column_names import CONST
from db.utils import strip_quote, load_csv
from db.database import run_with_session
from db.models import Area
from . import get_csv_path_for


CSV_PATH = get_csv_path_for("Prices_E_AreaCodes.csv")

table_name = "areas"


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
        Area.__table__.create(bind=session.bind, checkfirst=True)

        records = []
        for _, row in df.iterrows():
            records.append(
                {
                    CONST.DB.FAO_CODE: row[CONST.CSV.AREA_CODE],
                    CONST.DB.M49_CODE: row[CONST.CSV.M49_CODE],
                    CONST.DB.NAME: row[CONST.CSV.AREA_NAME],
                }
            )

        # Batch insert with conflict handling
        stmt = pg_insert(Area).values(records)
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
