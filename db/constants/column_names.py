class CSVColumns:
    """Constants for column names in FAO CSV files."""

    ITEM_CODE = "Item Code"
    ITEM_NAME = "Item"
    CPC_CODE = "CPC Code"
    AREA_NAME = "Area"
    AREA_CODE = "Area Code"
    M49_CODE = "M49 Code"
    YEAR = "Year"
    ITEM_UNIT = "Unit"
    ITEM_VALUE = "Value"
    ITEM_CURRENCY_TYPE = "Element"
    ITEM_PRICE_M49_CODE = "Area Code (M49)"
    CURRENCY = "Currency"
    CURRENCY_CODE = "ISO Currency Code"
    FLAG = "Flag"
    UNIT = "Unit"
    VALUE = "Value"
    MONTH_CODE = "Months Code"


class DBColumns:
    """Constants for column names in the database models."""

    FAO_CODE = "fao_code"
    CPC_CODE = "cpc_code"
    M49_CODE = "m49_code"
    ITEM_ID = "item_id"
    ITEM_NAME = "item_name"
    ITEM_CODE = "item_code"
    AREA_ID = "area_id"
    AREA_NAME = "area_name"
    AREA_CODE = "area_code"
    PRICE = "price"
    VALUE = "value"
    YEAR = "year"
    CURRENCY = "currency"
    CURRENCY_NAME = "currency_name"
    CURRENCY_CODE = "currency_code"
    NAME = "name"


class Constants:
    CSV = CSVColumns()
    DB = DBColumns()


CONST = Constants()
