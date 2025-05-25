from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class ItemPrice(Base):
    __tablename__ = "item_prices"
    __table_args__ = {"schema": "food"}

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("food.items.id"), nullable=False)
    area_id = Column(Integer, ForeignKey("food.areas.id"), nullable=False)
    value = Column(Integer)
    unit = Column(String)  # Currency
    year = Column(Integer, nullable=False)
    currency_type = Column(String, nullable=False)

    item = relationship("Item", back_populates="prices")
    area_rel = relationship("Area", back_populates="item_prices")

    def __repr__(self):
        return (
            f"<ItemPrice(item_id={self.ingredient_id}, value={self.value} {self.unit})>"
        )
