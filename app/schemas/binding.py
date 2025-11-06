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
    id: int
    chef_id: int
    customer_id: int
    chef_username: str
    customer_username: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
