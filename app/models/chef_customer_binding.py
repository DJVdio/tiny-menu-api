from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class BindingStatus(str, enum.Enum):
    PENDING = "pending"  # 待审批
    APPROVED = "approved"  # 已同意
    REJECTED = "rejected"  # 已拒绝
    UNBOUND = "unbound"  # 已解绑


class ChefCustomerBinding(Base):
    __tablename__ = "chef_customer_bindings"

    id = Column(Integer, primary_key=True)
    chef_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(BindingStatus), default=BindingStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    chef = relationship("User", foreign_keys=[chef_id], backref="customer_bindings")
    customer = relationship("User", foreign_keys=[customer_id], backref="chef_bindings")

    __table_args__ = (
        Index('idx_chef_status', 'chef_id', 'status'),  # 厨师查看待处理请求和已绑定顾客
        Index('idx_customer_chef', 'customer_id', 'chef_id'),  # 检查是否已存在绑定
        Index('idx_chef_customer_status', 'chef_id', 'customer_id', 'status'),  # 复合查询优化
    )
