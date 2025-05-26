from sqlalchemy import (
    Column,
    Integer,
    String,
    Index,
)
from sqlalchemy.orm import relationship
from db.database import Base


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # FAO Unique identifier for the area
    fao_code = Column(Integer, unique=True, nullable=False)
    # M49 Unique global identifier for the area
    m49_code = Column(String, unique=True, nullable=False)

    item_prices = relationship("ItemPrice", back_populates="area_rel")

    __table_args__ = (
        # fao_code and m49_code already unique individually
        Index("ix_area_fao_code", "fao_code"),
    )

    def __repr__(self):
        return f"<Area(name='{self.name}', area_code='{self.area_code}')>"
