from sqlalchemy import (
    Column,
    Integer,
    String,
    Index,
    Date,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from db.database import Base


class AnomalyDetail(Base):
    __tablename__ = "anomaly_details"

    id = Column(Integer, primary_key=True)
    anomaly_id = Column(Integer, ForeignKey("anomalies.id"), nullable=False)
    anomaly_type = Column(String(50), nullable=False)
    anomaly_date = Column(Date, nullable=False)
    details = Column(Text, nullable=False)

    anomaly = relationship("Anomaly", back_populates="details")

    __table_args__ = (
        Index("ix_anomaly_detail_anomaly_id", "anomaly_id"),
        Index("ix_anomaly_detail_type", "anomaly_type"),
        UniqueConstraint(
            "anomaly_id", "anomaly_type", "anomaly_date", name="uq_anomaly_detail_key"
        ),
    )

    def __repr__(self):
        return f"<AnomalyDetail(anomaly_id='{self.anomaly_id}', anomaly_type='{self.anomaly_type}', anomaly_date='{self.anomaly_date}', details='{self.details}')>"
