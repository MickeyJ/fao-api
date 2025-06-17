# templates/model.py.jinja2
from sqlalchemy import (
    String,
    SmallInteger,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Index,
    Column,
    func,
)
from fao.src.db.database import Base


class ValueSharesIndustryPrimaryFactors(Base):
    __tablename__ = "value_shares_industry_primary_factors"
     # Dataset table - use auto-increment id
    id = Column(Integer, primary_key=True)
    # Foreign key to area_codes
    area_code_id = Column(Integer, ForeignKey("area_codes.id"), index=True)
    # Foreign key to elements
    element_code_id = Column(Integer, ForeignKey("elements.id"), index=True)
    # Foreign key to flags
    flag_id = Column(Integer, ForeignKey("flags.id"), index=True)
    food_value_code = Column(String, nullable=False, index=False)
    food_value = Column(String, nullable=False, index=False)
    industry_code = Column(String, nullable=False, index=False)
    industry = Column(String, nullable=False, index=False)
    factor_code = Column(String, nullable=False, index=False)
    factor = Column(String, nullable=False, index=False)
    year_code = Column(String(8), nullable=False, index=False)
    year = Column(SmallInteger, nullable=False, index=True)
    unit = Column(String(50), nullable=False, index=False)
    value = Column(Float, nullable=False, index=False)
   
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    #     #         #         #             #         #             #         #             #         #         #             #         #         #         #         #             #             
    #         # __table_args__ = (
    #     Index("ix_19988524_uniq_uniq", 
    #         'area_code_id', 'element_code_id', 'flag_id', 'year', 'unit',
    #         unique=True),
    # )
    #         
    def __repr__(self):
        # Show first few columns for datasets
        return f"<ValueSharesIndustryPrimaryFactors(id={self.id})>"
