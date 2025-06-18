# templates/model.py.jinja2
from sqlalchemy import (
    String,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Index,
    Column,
    func,
)
from fao.src.db.database import Base


class WorldCensusAgriculture(Base):
    __tablename__ = "world_census_agriculture"
     # Dataset table - use auto-increment id
    id = Column(Integer, primary_key=True)
    # Foreign key to area_codes
    area_code_id = Column(Integer, ForeignKey("area_codes.id"), index=True)
    # Foreign key to item_codes
    item_code_id = Column(Integer, ForeignKey("item_codes.id"), index=True)
    # Foreign key to elements
    element_code_id = Column(Integer, ForeignKey("elements.id"), index=True)
    # Foreign key to flags
    flag_id = Column(Integer, ForeignKey("flags.id"), index=True)
    wca_round_code = Column(String, nullable=False, index=False)
    wca_round = Column(Integer, nullable=False, index=False)
    census_year_code = Column(String, nullable=False, index=False)
    census_year = Column(String, nullable=False, index=False)
    unit = Column(String(50), nullable=False, index=False)
    value = Column(Float, nullable=False, index=False)
    note = Column(String, index=False)
   
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    #     #         #         #             #         #             #         #             #         #             #         #         #             #         #         #         #         #             #             
    #         # __table_args__ = (
    #     Index("ix_eefb1a57_uniq_uniq", 
    #         'area_code_id', 'item_code_id', 'element_code_id', 'flag_id', 'year', 'unit',
    #         unique=True),
    # )
    #         
    def __repr__(self):
        # Show first few columns for datasets
        return f"<WorldCensusAgriculture(id={self.id})>"
