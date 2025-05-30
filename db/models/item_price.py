from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from db.database import Base


class ItemPrice(Base):
    __tablename__ = "item_prices"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    value = Column(Float)
    currency = Column(String)
    year = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    item = relationship("Item", back_populates="prices")
    area_rel = relationship("Area", back_populates="item_prices")

    __table_args__ = (
        UniqueConstraint(
            "item_id", "area_id", "value", "currency", "year", name="uq_item_price_key"
        ),
    )

    def __repr__(self):
        return (
            f"<ItemPrice(item_id={self.item_id}, value={self.value} {self.currency})>"
        )
