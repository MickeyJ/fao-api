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


class TradeDetailedTradeMatrix(Base):
    __tablename__ = "trade_detailed_trade_matrix"
     # Dataset table - use auto-increment id
    id = Column(Integer, primary_key=True)
    # Foreign key to reporter_country_codes
    reporter_country_code_id = Column(Integer, ForeignKey("reporter_country_codes.id"), index=True)
    # Foreign key to partner_country_codes
    partner_country_code_id = Column(Integer, ForeignKey("partner_country_codes.id"), index=True)
    # Foreign key to item_codes
    item_code_id = Column(Integer, ForeignKey("item_codes.id"), index=True)
    # Foreign key to elements
    element_code_id = Column(Integer, ForeignKey("elements.id"), index=True)
    # Foreign key to flags
    flag_id = Column(Integer, ForeignKey("flags.id"), index=True)
    year_code = Column(String(8), nullable=False, index=False)
    year = Column(SmallInteger, nullable=False, index=True)
    unit = Column(String(50), nullable=False, index=False)
    value = Column(Float, nullable=False, index=False)
   
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    #     #         #         #             #         #             #         #             #         #             #         #             #         #         #             #         #         #         #         #             #             
    #         # __table_args__ = (
    #     Index("ix_ee70210f_uniq_uniq", 
    #         'reporter_country_code_id', 'partner_country_code_id', 'item_code_id', 'element_code_id', 'flag_id', 'year', 'unit',
    #         unique=True),
    # )
    #         
    def __repr__(self):
        # Show first few columns for datasets
        return f"<TradeDetailedTradeMatrix(id={self.id})>"
