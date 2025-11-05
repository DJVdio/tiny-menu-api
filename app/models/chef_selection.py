from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class ChefSelection(Base):
    __tablename__ = "chef_selections"

    id = Column(Integer, primary_key=True, index=True)
    chef_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_selection_id = Column(Integer, ForeignKey("customer_selections.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    chef = relationship("User", foreign_keys=[chef_id])
    customer_selection = relationship("CustomerSelection")
    dish = relationship("Dish")
