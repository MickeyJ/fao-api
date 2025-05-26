from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Text,
    UniqueConstraint,
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

    __table_args__ = (
        UniqueConstraint("area_id", "year", "month", name="uq_price_index_key"),
        # Or if month can be null and you want one record per area/year:
        # UniqueConstraint('area_id', 'year', name='uq_price_index_key'),
    )

    def __repr__(self):
        return f"<FoodPriceIndex(area_id={self.area_id}, year={self.year}, value={self.value})>"
