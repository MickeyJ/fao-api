import calendar
from typing import Optional
from sqlalchemy import Column, Integer, Float, ForeignKey, Index, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UniqueConstraint
from db.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    value = Column(Float, nullable=False)
    year = Column(Integer, nullable=False)
    month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    @property
    def month_name(self):
        if self.month is None:
            return "Annual"
        return calendar.month_name[self.month]  # "January", "February", etc.

    @property
    def is_annual(self):
        return self.month is None

    __table_args__ = (
        Index("ix_exchange_rate_area_id", "area_id"),
        Index("ix_exchange_rate_currency_id", "currency_id"),
        UniqueConstraint(
            "area_id", "currency_id", "year", "month", name="uq_exchange_rate_key"
        ),
    )

    def __repr__(self):
        return f"<ExchangeRate(area_id={self.area_id}, currency_id={self.currency_id}, value={self.value}, year={self.year}, month={self.month})>"
