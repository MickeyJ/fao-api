import pandas as pd


def strip_quote(df: pd.DataFrame, column_name, quote="'"):
    return df[column_name].str.replace(quote, "").str.strip()
