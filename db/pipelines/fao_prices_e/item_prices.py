import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from db.constants.column_names import CONST
from db.utils import strip_quote, load_csv
from db.database import run_with_session
from . import get_csv_path_for, standardize_currency_by_m49
from db.models import ItemPrice, Item, Area

CSV_PATH = get_csv_path_for("Prices_E_All_Data_(Normalized).csv")

table_name = "item_prices"


def load():
    return load_csv(CSV_PATH)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with missing or malformed data"""
    if df.empty:
        print(f"No {table_name} data to clean.")
        return df

    print(f"\nCleaning {table_name} data...")
    initial_count = len(df)

    # Filter out price indices (Element Code 5539)
    df = df[df["Element Code"] == "5532"].copy()
    # df = df[df["Flag"] == "A"].copy()
    price_count = len(df)
    index_count = initial_count - price_count

    print(f"\nFiltered out Element Code 5539: {initial_count:,} → {price_count:,} rows")
    print(f"Excluded {index_count:,} price index rows")

    df = df[
        [
            CONST.CSV.ITEM_CODE,
            CONST.CSV.AREA_CODE,
            CONST.CSV.AREA_NAME,
            CONST.CSV.ITEM_PRICE_M49_CODE,
            CONST.CSV.ITEM_VALUE,
            CONST.CSV.ITEM_UNIT,
            CONST.CSV.YEAR,
            CONST.CSV.ITEM_CURRENCY_TYPE,
        ]
    ].copy()

    # fill in missing item unit based on area code
    # df[ITEM_UNIT] = df.groupby([AREA_CODE])[ITEM_UNIT].ffill().bfill()

    # Identify rows that will be dropped for missing data
    dropped_mask = df[
        df[CONST.CSV.ITEM_VALUE].isna()
        | df[CONST.CSV.ITEM_UNIT].isna()
        | df[CONST.CSV.YEAR].isna()
    ]

    print(f"\nRows to be dropped for missing data: {len(dropped_mask)}")
    if len(dropped_mask) > 0:
        print("Sample dropped rows:")
        print(dropped_mask.head(2))

    # Then apply the filter
    df = df.dropna(
        subset=[CONST.CSV.ITEM_VALUE, CONST.CSV.ITEM_UNIT, CONST.CSV.YEAR]
    ).copy()

    # strip out any single quotes and ensure type
    df[CONST.CSV.ITEM_CODE] = strip_quote(df, CONST.CSV.ITEM_CODE).astype(int)
    df[CONST.CSV.AREA_CODE] = strip_quote(df, CONST.CSV.AREA_CODE).astype(int)
    df[CONST.CSV.ITEM_PRICE_M49_CODE] = strip_quote(
        df, CONST.CSV.ITEM_PRICE_M49_CODE
    ).astype(str)

    # ensure item value is an float
    df[CONST.CSV.ITEM_VALUE] = df[CONST.CSV.ITEM_VALUE].str.strip().astype(float)

    # ensure year is an integer
    df[CONST.CSV.YEAR] = df[CONST.CSV.YEAR].str.strip().astype(int)

    # strip whitespace from unit
    df[CONST.CSV.ITEM_UNIT] = df[CONST.CSV.ITEM_UNIT].astype(str).str.strip()

    # replace FAO units (LCU, SLC, USD) with country specific currency units
    df = standardize_currency_by_m49(
        df, CONST.CSV.ITEM_PRICE_M49_CODE, CONST.CSV.ITEM_UNIT
    )

    # strip whitespace from currency type
    df[CONST.CSV.ITEM_CURRENCY_TYPE] = (
        df[CONST.CSV.ITEM_CURRENCY_TYPE].astype(str).str.strip()
    )

    print(df.head(10))

    final_count = len(df)
    print(f"\nValidated {table_name} items: {initial_count} → {final_count} rows")

    return df


def insert(df: pd.DataFrame, session: Session):
    """Insert items into the database."""
    if df.empty:
        print(f"No {table_name} data to insert.")
        return

    print(f"\nPreparing chunked bulk {table_name} insert...")

    try:
        # Ensure the Area table exists
        ItemPrice.__table__.create(bind=session.bind, checkfirst=True)

        # Get mappings of FAO codes to database IDs
        items_map = {item.fao_code: item.id for item in session.query(Item).all()}
        areas_map = {area.fao_code: area.id for area in session.query(Area).all()}

        print(f"\nFound {len(items_map)} items and {len(areas_map)} areas in database")

        CHUNK_SIZE = 5000  # Adjust based on performance
        total_inserted = 0
        total_skipped = 0

        for i in range(0, len(df), CHUNK_SIZE):
            chunk = df.iloc[i : i + CHUNK_SIZE]

            records = []
            skipped = 0
            for _, row in chunk.iterrows():
                item_id = items_map.get(row[CONST.CSV.ITEM_CODE])
                area_id = areas_map.get(row[CONST.CSV.AREA_CODE])

                if item_id is not None and area_id is not None:
                    records.append(
                        {
                            CONST.DB.ITEM_ID: item_id,
                            CONST.DB.AREA_ID: area_id,
                            CONST.DB.VALUE: row[CONST.CSV.ITEM_VALUE],
                            CONST.DB.CURRENCY: row[CONST.CSV.ITEM_UNIT],
                            CONST.DB.YEAR: row[CONST.CSV.YEAR],
                        }
                    )
                else:
                    skipped += 1

            if records:
                stmt = pg_insert(ItemPrice).values(records)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=[
                        CONST.DB.ITEM_ID,
                        CONST.DB.AREA_ID,
                        CONST.DB.VALUE,
                        CONST.DB.CURRENCY,
                        CONST.DB.YEAR,
                    ]
                )
                session.execute(stmt)
                session.commit()

            total_inserted += len(records)
            total_skipped += skipped
            print(
                f"Processed chunk {i//CHUNK_SIZE + 1}: {total_inserted:,} inserted, {total_skipped:,} skipped"
            )

        print(
            f"✅ {table_name} insert complete: {total_inserted:,} inserted, {total_skipped:,} skipped"
        )
    except Exception as e:
        print(f"Error inserting {table_name}: {e}")
        session.rollback()


def run(db):
    df = load()
    df = clean(df)
    insert(df, db)


if __name__ == "__main__":
    run_with_session(run)
