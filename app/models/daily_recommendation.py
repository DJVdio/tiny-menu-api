from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class DailyRecommendation(Base):
    __tablename__ = "daily_recommendations"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    dish = relationship("Dish")

    __table_args__ = (
        Index('idx_date', 'date'),  # 查询今日推荐
        Index('idx_date_dish', 'date', 'dish_id'),  # 确保同一天不会推荐重复菜品
    )
