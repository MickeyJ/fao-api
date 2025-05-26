import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert


from db.constants.column_names import (
    ITEM_VALUE,
    ITEM_UNIT,
    YEAR,
    ITEM_CURRENCY_TYPE,
    ITEM_CODE,
    AREA_CODE,
    AREA_NAME,
    ITEM_PRICE_M49_CODE,
)

from db.database import run_with_session
from . import get_data_from, strip_quote, standardize_currency_by_m49
from db.models import ItemPrice, Item, Area

CSV = get_data_from("Prices_E_All_Data_(Normalized).csv")


def load():
    """Load and preview item price data."""
    print(f"\nLoading: {CSV}")
    df = pd.read_csv(CSV, dtype=str)
    df.columns = df.columns.str.strip()  # Clean up whitespace

    print(f"\nData shape: {df.shape}")
    print("Columns:", df.columns.tolist())
    print("\nElement types in your data:")
    print(df["Element Code"].value_counts())
    print("\nFirst 5 rows:")
    print(df.head(5))
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with missing or malformed data"""
    print("\nCleaning data...")
    initial_count = len(df)

    # Filter out price indices (Element Code 5539)
    df = df[df["Element Code"] != "5539"].copy()
    price_count = len(df)
    index_count = initial_count - price_count

    print(f"\nFiltered out Element Code 5539: {initial_count:,} → {price_count:,} rows")
    print(f"Excluded {index_count:,} price index rows")

    df = df[
        [
            ITEM_CODE,
            AREA_CODE,
            AREA_NAME,
            ITEM_PRICE_M49_CODE,
            ITEM_VALUE,
            ITEM_UNIT,
            YEAR,
            ITEM_CURRENCY_TYPE,
        ]
    ].copy()

    # fill in missing item unit based on area code
    # df[ITEM_UNIT] = df.groupby([AREA_CODE])[ITEM_UNIT].ffill().bfill()

    # Identify rows that will be dropped for missing data
    dropped_mask = df[df[ITEM_VALUE].isna() | df[ITEM_UNIT].isna() | df[YEAR].isna()]

    print(f"\nRows to be dropped for missing data: {len(dropped_mask)}")
    if len(dropped_mask) > 0:
        print("Sample dropped rows:")
        print(dropped_mask.head(2))

    # Then apply the filter
    df = df.dropna(subset=[ITEM_VALUE, ITEM_UNIT, YEAR]).copy()

    # strip out any single quotes and ensure type
    df[ITEM_CODE] = strip_quote(df, ITEM_CODE).astype(int)
    df[AREA_CODE] = strip_quote(df, AREA_CODE).astype(int)
    df[ITEM_PRICE_M49_CODE] = strip_quote(df, ITEM_PRICE_M49_CODE).astype(str)

    # ensure item value is an float
    df[ITEM_VALUE] = df[ITEM_VALUE].str.strip().astype(float)

    # ensure year is an integer
    df[YEAR] = df[YEAR].str.strip().astype(int)

    # strip whitespace from unit
    df[ITEM_UNIT] = df[ITEM_UNIT].astype(str).str.strip()

    # replace FAO units (LCU, SLC, USD) with country specific currency units
    df = standardize_currency_by_m49(df, ITEM_PRICE_M49_CODE, ITEM_UNIT)

    # strip whitespace from currency type
    df[ITEM_CURRENCY_TYPE] = df[ITEM_CURRENCY_TYPE].astype(str).str.strip()

    print(df.head(10))

    final_count = len(df)
    print(f"\nValidated items: {initial_count} → {final_count} rows")

    return df


def insert(df: pd.DataFrame, session: Session):
    """Insert items into the database."""
    print("\nPreparing chunked bulk insert...")

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
            item_id = items_map.get(row[ITEM_CODE])
            area_id = areas_map.get(row[AREA_CODE])

            if item_id is not None and area_id is not None:
                records.append(
                    {
                        "item_id": item_id,
                        "area_id": area_id,
                        "value": row[ITEM_VALUE],
                        "currency": row[ITEM_UNIT],
                        "year": row[YEAR],
                    }
                )
            else:
                skipped += 1

        if records:
            stmt = pg_insert(ItemPrice.__table__).values(records)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["item_id", "area_id", "year"]
            )
            session.execute(stmt)
            session.commit()

        total_inserted += len(records)
        total_skipped += skipped
        print(
            f"Processed chunk {i//CHUNK_SIZE + 1}: {total_inserted:,} inserted, {total_skipped:,} skipped"
        )

    print(f"✅ Complete: {total_inserted:,} inserted, {total_skipped:,} skipped")


def run(db):
    df = load()
    df = clean(df)
    insert(df, db)


if __name__ == "__main__":
    run_with_session(run)
