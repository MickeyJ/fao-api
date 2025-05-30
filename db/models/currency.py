from sqlalchemy import Column, Integer, String, Index, DateTime, func
from db.database import Base


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True)
    currency_code = Column(String, unique=True, nullable=False)
    currency_name = Column(String, nullable=False)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (Index("ix_currency_code", "currency_code"),)

    def __repr__(self):
        return f"<Currency(currency_code='{self.currency_code}', currency_name='{self.currency_name}')>"
