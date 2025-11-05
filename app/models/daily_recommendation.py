from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class DailyRecommendation(Base):
    __tablename__ = "daily_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    dish = relationship("Dish")
