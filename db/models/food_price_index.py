from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from db.database import Base


class FoodPriceIndex(Base):
    __tablename__ = "food_price_index"

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=True)
    value = Column(Float, nullable=False)
    note = Column(Text, nullable=True)
    flag = Column(String(1), nullable=True)

    area = relationship("Area")

    def __repr__(self):
        return f"<FoodPriceIndex(area_id={self.area_id}, year={self.year}, value={self.value})>"
