from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from collections import defaultdict
from db.database import get_db
from db.models import Item, Area, ItemPrice

app = FastAPI()


@app.get("/")
def root():
    return {"message": "FastAPI is live!"}


@app.get("/items")
def get_items(limit: int = 5000, db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(
                Item.id.label("item_id"),
                Item.name.label("item_name"),
                Area.id.label("area_id"),
                Area.name.label("area_name"),
                func.json_agg(
                    func.json_build_object(
                        "year", ItemPrice.year, "price", ItemPrice.value
                    )
                ).label("prices"),
            )
            .join(Item, Item.id == ItemPrice.item_id)
            .join(Area, Area.id == ItemPrice.area_id)
            .group_by(Item.id, Item.name, Area.id, Area.name)
            .order_by(Item.name, Area.name)
            .limit(limit)
        )
        .mappings()
        .all()
    )

    return [
        {
            "item_name": row["item_name"],
            "area_name": row["area_name"],
            "prices": row["prices"],  # Already aggregated as JSON
        }
        for row in rows
    ]


# Make it runnable with: python -m api
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.__main__:app", host="localhost", port=8000, reload=True)
