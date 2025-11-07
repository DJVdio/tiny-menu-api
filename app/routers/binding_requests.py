"""
绑定请求路由
提供 /api/binding-requests 路径的绑定管理接口
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.user import User
from ..schemas.binding import BindingCreate, BindingUpdate, BindingResponse
from ..utils.auth import get_current_user
from ..services import binding_service

router = APIRouter(prefix="/api/binding-requests", tags=["绑定请求"])


@router.get("", response_model=List[BindingResponse])
async def get_binding_requests(
    chefId: Optional[str] = Query(None, description="厨师ID，用于过滤绑定请求"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询绑定请求列表
    作为厨师身份查看发送给自己的待处理绑定请求

    Args:
        chefId: 厨师ID（可选），用于过滤绑定请求，必须与当前用户ID匹配
        current_user: 当前登录用户（依赖注入）
        db: 数据库会话（依赖注入）

    Returns:
        List[BindingResponse]: 待处理的绑定请求列表

    Raises:
        403: 尝试查看其他厨师的绑定请求
    """
    # 如果提供了 chefId，验证是否匹配当前用户
    if chefId and str(current_user.id) != chefId:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own binding requests"
        )

    return binding_service.get_pending_bindings_for_chef(db, current_user)


@router.post("", response_model=BindingResponse, status_code=status.HTTP_201_CREATED)
async def create_binding_request(
    binding_data: BindingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建绑定请求
    作为顾客身份申请绑定目标用户（目标用户将作为厨师身份）

    Args:
        binding_data: 绑定数据，包含chef_username（要绑定的厨师用户名）
        current_user: 当前登录用户（依赖注入）
        db: 数据库会话（依赖注入）

    Returns:
        BindingResponse: 创建的绑定请求信息

    Raises:
        404: 目标用户不存在
        400: 不能绑定自己或已存在绑定关系
    """
    return binding_service.create_binding_request(db, current_user, binding_data.chef_username)


@router.put("/{request_id}", response_model=BindingResponse)
async def update_binding_request(
    request_id: str,
    binding_update: BindingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新绑定请求状态（接受或拒绝）
    作为厨师身份处理发送给自己的绑定请求
    支持状态值：'accepted' 或 'rejected'（会自动映射到内部的 'approved' 或 'rejected'）

    Args:
        request_id: 绑定请求ID（字符串格式）
        binding_update: 更新数据，包含status（'accepted'或'rejected'）
        current_user: 当前登录用户（依赖注入）
        db: 数据库会话（依赖注入）

    Returns:
        BindingResponse: 更新后的绑定请求信息

    Raises:
        400: 请求ID格式无效
        404: 绑定请求不存在
        400: 绑定请求状态不是pending或新状态无效
    """
    # 验证request_id格式
    try:
        binding_id = int(request_id)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID"
        )

    return binding_service.update_binding_status(db, binding_id, current_user, binding_update.status)
