from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Index, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class SelectionStatus(str, enum.Enum):
    ACTIVE = "active"  # 生效中
    CANCELLED = "cancelled"  # 已取消


class CustomerSelection(Base):
    __tablename__ = "customer_selections"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(Enum(SelectionStatus), default=SelectionStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联
    user = relationship("User")
    dish = relationship("Dish")

    __table_args__ = (
        Index('idx_user_date', 'user_id', 'date'),  # 查询用户今日选菜
        Index('idx_date_user', 'date', 'user_id'),  # 按日期查询所有选菜
        Index('idx_user_dish_date_status', 'user_id', 'dish_id', 'date', 'status'),  # 检查是否重复选择（加入状态）
    )
