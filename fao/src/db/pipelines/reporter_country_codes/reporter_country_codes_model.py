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


class ReporterCountryCodes(Base):
    __tablename__ = "reporter_country_codes"
    # Reference table - use domain primary key
    id = Column(Integer, primary_key=True)
    reporter_country_code = Column(String, nullable=False, index=False)
    reporter_countries = Column(String, nullable=False, index=False)
    reporter_country_code_m49 = Column(String, nullable=False, index=False)
    source_dataset = Column(String, nullable=False, index=False)
   
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Composite indexes for reference tables
    __table_args__ = (
        Index("ix_reporter_reporter_src", 'reporter_country_code', 'source_dataset', unique=True),
    )
    # TODO: Indices for dataset tables
    #     
    def __repr__(self):
        return f"<ReporterCountryCodes(reporter_country_code={self.reporter_country_code})>"
