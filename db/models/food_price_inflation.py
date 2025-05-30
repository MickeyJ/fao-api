from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Text,
    UniqueConstraint,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship
from db.database import Base


class FoodPriceInflation(Base):
    __tablename__ = "food_price_inflation"

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=True)
    value = Column(Float, nullable=False)
    note = Column(Text, nullable=True)
    flag = Column(String(1), nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    area = relationship("Area")

    __table_args__ = (
        UniqueConstraint("area_id", "year", "month", name="uq_price_inflation_key"),
        # Or without month if needed:
        # UniqueConstraint('area_id', 'year', name='uq_price_inflation_key'),
    )

    def __repr__(self):
        return f"<FoodPriceInflation(area_id={self.area_id}, year={self.year}, value={self.value})>"
