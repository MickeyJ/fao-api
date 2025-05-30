from sqlalchemy import (
    Column,
    Integer,
    Index,
    ForeignKey,
    UniqueConstraint,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship
from db.database import Base


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    details = relationship("AnomalyDetail", back_populates="anomaly")

    __table_args__ = (
        # fao_code and m49_code already unique individually
        Index("ix_anomaly_area_id", "area_id"),
        Index("ix_anomaly_item_id", "item_id"),
        UniqueConstraint("area_id", "item_id", name="uq_anomaly_key"),
    )

    def __repr__(self):
        return f"<Anomaly(item_id='{self.item_id}', area_id='{self.area_id}')>"
