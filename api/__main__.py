from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db.models.item import Item

app = FastAPI()


@app.get("/")
def root():
    return {"message": "FastAPI is live!"}


@app.get("/items")
def get_items(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Item).limit(limit).all()


# Make it runnable with: python -m api
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.__main__:app", host="localhost", port=8000, reload=True)
