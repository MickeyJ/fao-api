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


class FoodValues(Base):
    __tablename__ = "food_values"
    # Reference table - use domain primary key
    id = Column(Integer, primary_key=True)
    food_value_code = Column(String, nullable=False, index=False)
    food_value = Column(String, nullable=False, index=False)
    source_dataset = Column(String, nullable=False, index=False)
   
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Composite indexes for reference tables
    __table_args__ = (
        Index("ix_food_val_food_val_src", 'food_value_code', 'source_dataset', unique=True),
    )
    # TODO: Indices for dataset tables
    #     
    def __repr__(self):
        return f"<FoodValues(food_value_code={self.food_value_code})>"
