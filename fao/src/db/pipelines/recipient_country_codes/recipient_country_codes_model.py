# templates/model.py.jinja2
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Index,
    Column,
    func,
)
from fao.src.db.database import Base


class RecipientCountryCodes(Base):
    __tablename__ = "recipient_country_codes"
    # Reference table - use domain primary key
    id = Column(Integer, primary_key=True)
    recipient_country_code = Column(String, nullable=False, index=False)
    recipient_country = Column(String, nullable=False, index=False)
    recipient_country_code_m49 = Column(String, nullable=False, index=False)
    source_dataset = Column(String, nullable=False, index=False)
   
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Composite indexes for reference tables
    __table_args__ = (
        Index("ix_recipien_recipien_src", 'recipient_country_code', 'source_dataset', unique=True),
    )
    # TODO: Indices for dataset tables
    #     
    def __repr__(self):
        return f"<RecipientCountryCodes(recipient_country_code={self.recipient_country_code})>"
