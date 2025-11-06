from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """用户基础信息"""
    username: str  # 登录用户名
    nickname: str  # 显示昵称


class UserCreate(UserBase):
    """用户注册数据"""
    password: str


class UserLogin(BaseModel):
    """用户登录数据"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户信息响应"""
    id: str  # 用户ID
    username: str  # 用户名
    name: str  # 昵称（显示名称）
    created_at: Optional[datetime] = None  # 创建时间

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT认证令牌响应"""
    user: UserResponse  # 用户基本信息
    token: str  # JWT访问令牌
