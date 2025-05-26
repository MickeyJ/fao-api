from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db.models.item import Item  # Example model

app = FastAPI()


@app.get("/")
def root():
    return {"message": "API is up!"}


@app.get("/items")
def list_items(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Item).limit(limit).all()
