from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Index, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class ChefSelectionStatus(str, enum.Enum):
    ACTIVE = "active"  # 生效中
    CANCELLED = "cancelled"  # 已取消


class ChefSelection(Base):
    __tablename__ = "chef_selections"

    id = Column(Integer, primary_key=True)
    chef_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_selection_id = Column(Integer, ForeignKey("customer_selections.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(Enum(ChefSelectionStatus), default=ChefSelectionStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联
    chef = relationship("User", foreign_keys=[chef_id])
    customer_selection = relationship("CustomerSelection")
    dish = relationship("Dish")

    __table_args__ = (
        Index('idx_chef_date', 'chef_id', 'date'),  # 查询厨师今日选择
        Index('idx_chef_customer_selection_status', 'chef_id', 'customer_selection_id', 'date', 'status'),  # 检查是否重复选择（加入状态）
    )
