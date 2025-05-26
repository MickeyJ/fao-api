import pandas as pd
from pathlib import Path

from db.constants.currency_codes import M49_TO_CURRENCY
from db.database import SessionLocal

# DATA_DIR = "https://food-oasis-data.s3.amazonaws.com/Prices_E_All_Data_(Normalized)"
DATA_DIR = Path(
    r"C:\Users\18057\Documents\Data\Food_FAO\Organized\Prices_E_All_Data_(Normalized)"
)


def strip_quote(df: pd.DataFrame, column_name, quote="'"):
    return df[column_name].str.replace(quote, "").str.strip()


def get_data_from(filename):
    return f"{DATA_DIR}/{filename}"


def run_with_session(fn):
    session = SessionLocal()
    try:
        fn(session)
    finally:
        session.close()


def standardize_currency_by_m49(df, m49_code_col, unit_col):
    """Replace ALL units with specific currency codes based on M49 country codes."""
    print("\nStandardizing all currency units using M49 codes...")

    initial_count = len(df)

    # Clean M49 codes (remove quotes and apostrophes)
    df[m49_code_col] = (
        df[m49_code_col]
        .astype(str)
        .str.replace("'", "")
        .str.replace('"', "")
        .str.strip()
    )

    # Show original unit distribution
    print("\nOriginal unit distribution:")
    original_units = df[unit_col].value_counts()
    print(original_units.head(10))

    # Replace ALL units with currency based on M49 code
    df[unit_col] = df[m49_code_col].map(M49_TO_CURRENCY)

    # Check for any unmapped areas
    unmapped_count = df[unit_col].isna().sum()
    if unmapped_count > 0:
        unmapped_areas = df.loc[df[unit_col].isna(), m49_code_col].unique()
        print(f"\n⚠️  Warning: {unmapped_count} rows with unmapped M49 codes:")
        print(f"   M49 codes: {unmapped_areas}")
        # Fill unmapped with 'LCU' as fallback
        df[unit_col] = df[unit_col].fillna("LCU")

    # Show final unit distribution
    print("\nFinal currency distribution:")
    final_units = df[unit_col].value_counts()
    print(final_units.head(10))

    print(f"\n✅ Standardized {initial_count:,} rows to country-specific currencies")

    return df
