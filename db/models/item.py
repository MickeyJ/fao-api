from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # FAO Unique identifier for the item
    fao_code = Column(Integer, unique=True, nullable=False)
    # UN's Central Product Classification (CPC) code
    cpc_code = Column(String, unique=True, nullable=False)

    prices = relationship("ItemPrice", back_populates="item")

    def __repr__(self):
        return f"<Item(id={self.id}, cpc_code='{self.cpc_code}', name='{self.name}')>"
