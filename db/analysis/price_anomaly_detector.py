import pandas as pd
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, text
from db.database import get_db
from db.models import Item, Area, ItemPrice


item_id = "item_id"
item_name = "item_name"
item_code = "item_code"
area_id = "area_id"
area_name = "area_name"
area_code = "area_code"
price = "price"
year = "year"


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
            Item.id.label(item_id),
            Item.name.label(item_name),
            Item.fao_code.label(item_code),
            Area.id.label(area_id),
            Area.name.label(area_name),
            Area.fao_code.label(area_code),
            ItemPrice.value.label(price),
            ItemPrice.currency,
            ItemPrice.year,
        )
        .join(ItemPrice, Item.id == ItemPrice.item_id)
        .join(Area, ItemPrice.area_id == Area.id)
        .order_by(Area.id, Item.id, ItemPrice.year)
        .limit(row_limit)
    )

    results = db.execute(query).mappings().all()

    # Convert results to DataFrame
    df = pd.DataFrame(results)

    if df.empty:
        return None

    df = df.groupby([area_code, item_code])

    anomalies = []

    # loop area/item group
    for columns, group in df:
        area_name_value = group.iloc[0][area_name]
        item_name_value = group.iloc[0][item_name]
        area_id_value = group.iloc[0][area_id]
        item_id_value = group.iloc[0][item_id]
        print(f"\n\nProcessing: {area_name_value} - {item_name_value}")

        flag_anomaly = False

        # loop area/item prices
        p = None  # previous
        for _, c in group.iterrows():
            if p is None:
                p = c
                continue

            # if ()
            # print("")
            # log_row(p, "Previous")
            percent_change = round(((c[price] - p[price]) / p[price]) * 100, 1)
            log_row(c, "Current ", f"  |  {percent_change}%")

            if abs(percent_change) >= percent_change_threshold:
                flag_anomaly = True
                anomalies.append(
                    {
                        "area_name": area_name_value,
                        "item_name": item_name_value,
                        "from_year": int(p[year]),
                        "to_year": int(c[year]),
                        "from_price": float(p[price]),
                        "to_price": float(c[price]),
                        "percent_change": percent_change,
                        "year_gap": int(c[year]) - int(p[year]),
                    }
                )
                break
            p = c

        if flag_anomaly:
            print(f"Recording Anomaly")

    # Save results to JSON
    output_data = {
        "detection_run": {
            "timestamp": datetime.now().isoformat(),
            "threshold_percent": percent_change_threshold,
            "total_checked": len(df),
            "total_anomalies": len(anomalies),
        },
        "anomalies": anomalies,
    }

    filename = (
        f"reports/price_anomalies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(filename, "w") as f:
        json.dump(output_data, f, indent=2)


def log_row(r, title: str, extra: str = ""):
    print(f"{title}: {r[year]} - {r[price]}{extra}")
