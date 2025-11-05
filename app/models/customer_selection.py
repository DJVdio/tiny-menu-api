from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class CustomerSelection(Base):
    __tablename__ = "customer_selections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    user = relationship("User")
    dish = relationship("Dish")
