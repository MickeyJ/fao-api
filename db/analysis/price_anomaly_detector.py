import pandas as pd
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from db.database import get_db
from db.models import Item, Area, ItemPrice, Anomaly
from db.constants.column_names import CONST


def detect_price_anomalies(db: Session):
    """
    Detect price anomalies in the food price database.
    Args: db (Session): SQLAlchemy session.
    Returns:
        pd.DataFrame: DataFrame containing items with detected price anomalies.
    """

    row_limit = 100  # Limit the number of rows to process
    percent_change_threshold = 50  # 50% change threshold for anomaly detection

    # Query to get item prices
    query = (
        select(
            Item.id.label(CONST.DB.ITEM_ID),
            Item.name.label(CONST.DB.ITEM_NAME),
            Item.fao_code.label(CONST.DB.ITEM_CODE),
            Area.id.label(CONST.DB.AREA_ID),
            Area.name.label(CONST.DB.AREA_NAME),
            Area.fao_code.label(CONST.DB.AREA_CODE),
            ItemPrice.value.label(CONST.DB.PRICE),
            ItemPrice.currency,
            ItemPrice.year.label(CONST.DB.YEAR),
        )
        .join(ItemPrice, Item.id == ItemPrice.item_id)
        .join(Area, ItemPrice.area_id == Area.id)
        .outerjoin(Anomaly, (Anomaly.item_id == Item.id) & (Anomaly.area_id == Area.id))
        .where(Anomaly.id.is_(None))  # Only items/areas without existing anomalies
        .order_by(Area.id, Item.id, ItemPrice.year)
        # .limit(row_limit)
    )

    results = db.execute(query).mappings().all()

    # Convert results to DataFrame
    df = pd.DataFrame(results)

    if df.empty:
        return None

    df = df.groupby([CONST.DB.AREA_CODE, CONST.DB.ITEM_CODE])

    anomalies = []

    # loop area/item group
    for columns, group in df:
        area_name_value = group.iloc[0][CONST.DB.AREA_NAME]
        item_name_value = group.iloc[0][CONST.DB.ITEM_NAME]
        print(f"\nProcessing: {area_name_value} - {item_name_value}")

        flag_anomaly = False

        # loop area/item prices
        p = None  # previous
        for _, c in group.iterrows():
            if p is None:
                p = c
                continue

            percent_change = round(
                ((c[CONST.DB.PRICE] - p[CONST.DB.PRICE]) / p[CONST.DB.PRICE]) * 100, 1
            )
            # log_row(c, "Current ", f"  |  {percent_change}%")

            if abs(percent_change) >= percent_change_threshold:
                print(f"Found Anomaly")
                anomalies.append(
                    {
                        CONST.DB.AREA_NAME: c[CONST.DB.AREA_NAME],
                        CONST.DB.ITEM_NAME: c[CONST.DB.ITEM_NAME],
                        CONST.DB.ITEM_ID: int(c[CONST.DB.ITEM_ID]),
                        CONST.DB.AREA_ID: int(c[CONST.DB.AREA_ID]),
                        "from_year": int(p[CONST.DB.YEAR]),
                        "to_year": int(c[CONST.DB.YEAR]),
                        "from_price": float(p[CONST.DB.PRICE]),
                        "to_price": float(c[CONST.DB.PRICE]),
                        "percent_change": percent_change,
                        "year_gap": int(c[CONST.DB.YEAR]) - int(p[CONST.DB.YEAR]),
                    }
                )
                break
            p = c

    if not anomalies:
        print("No anomalies detected.")
        return None

    insert_anomalies_batch(db, anomalies)

    # save_anomalies_to_json(
    #     anomalies,
    #     f"reports/price_anomalies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    # )


def log_row(r, title: str, extra: str = ""):
    print(f"{title}: {r[CONST.DB.YEAR]} - {r[CONST.DB.PRICE]}{extra}")


def insert_anomalies_batch(db: Session, anomalies: list):
    """
    Batch insert detected anomalies into the database.
    Args:
        db (Session): SQLAlchemy session.
        anomalies (list): List of anomaly dictionaries.
    """
    if not anomalies:
        return

    try:
        # Prepare batch data
        batch_data = []
        for anomaly in anomalies:
            batch_data.append(
                {
                    CONST.DB.ITEM_ID: anomaly[CONST.DB.ITEM_ID],
                    CONST.DB.AREA_ID: anomaly[CONST.DB.AREA_ID],
                }
            )

        print(f"Batch inserting {len(batch_data)} anomalies...")
        # print(f"{batch_data}")
        # Batch insert with conflict resolution
        stmt = pg_insert(Anomaly).values(batch_data)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=[CONST.DB.AREA_ID, CONST.DB.ITEM_ID]
        )
        result = db.execute(stmt)
        db.commit()

        print(
            f"✅ Batch inserted {result.rowcount} anomalies (out of {len(anomalies)} detected)"
        )

    except Exception as e:
        print(f"❌ Error in batch insert: {e}")
        db.rollback()
        raise


def save_anomalies_to_json(anomalies: list, filename: str):
    """
    Save detected anomalies to a JSON file.
    Args:
        anomalies (list): List of anomaly dictionaries.
        filename (str): Output filename.
    """
    output_data = {
        "detection_run": {
            "timestamp": datetime.now().isoformat(),
            "total_anomalies": len(anomalies),
        },
        "anomalies": anomalies,
    }

    with open(filename, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"Anomalies saved to {filename}")
