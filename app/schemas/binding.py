from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BindingCreate(BaseModel):
    """创建绑定请求 - 顾客申请绑定厨师"""
    chef_username: str


class BindingUpdate(BaseModel):
    """更新绑定状态 - 厨师同意或拒绝"""
    status: str  # "approved" or "rejected"


class BindingResponse(BaseModel):
    """绑定关系响应"""
    id: str  # 绑定记录ID
    customerId: str  # 顾客ID
    customerName: str  # 顾客姓名
    chefId: str  # 厨师ID
    chefName: str  # 厨师姓名
    status: str  # 绑定状态：pending（待审批）、approved（已同意）、rejected（已拒绝）
    createdAt: str  # 创建时间（ISO 8601格式）
    updatedAt: Optional[str] = None  # 更新时间（ISO 8601格式）

    class Config:
        from_attributes = True
        populate_by_name = True
