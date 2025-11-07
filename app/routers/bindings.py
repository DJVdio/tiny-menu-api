from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..schemas.binding import BindingCreate, BindingUpdate, BindingResponse
from ..utils.auth import get_current_user
from ..services import binding_service

router = APIRouter(prefix="/api/bindings", tags=["绑定关系"])


@router.post("/request", response_model=BindingResponse, status_code=status.HTTP_201_CREATED)
async def request_binding(
    binding_data: BindingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    申请绑定另一个用户
    当前用户作为顾客身份，申请绑定目标用户（目标用户将作为厨师身份）

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


@router.get("/pending", response_model=List[BindingResponse])
async def get_pending_bindings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查看待处理的绑定请求
    作为厨师身份查看发送给自己的绑定请求

    Args:
        current_user: 当前登录用户（依赖注入）
        db: 数据库会话（依赖注入）

    Returns:
        List[BindingResponse]: 待处理的绑定请求列表
    """
    return binding_service.get_pending_bindings_for_chef(db, current_user)


@router.put("/{binding_id}", response_model=BindingResponse)
async def update_binding_status(
    binding_id: int,
    binding_update: BindingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    同意或拒绝绑定请求
    作为厨师身份处理发送给自己的绑定请求

    Args:
        binding_id: 绑定请求ID
        binding_update: 更新数据，包含status（'approved'或'rejected'）
        current_user: 当前登录用户（依赖注入）
        db: 数据库会话（依赖注入）

    Returns:
        BindingResponse: 更新后的绑定请求信息

    Raises:
        404: 绑定请求不存在
        400: 绑定请求状态不是pending或新状态无效
    """
    return binding_service.update_binding_status(db, binding_id, current_user, binding_update.status)


@router.get("/my-bindings", response_model=List[BindingResponse])
async def get_my_bindings(
    as_chef: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询我的绑定关系

    Args:
        as_chef: 是否作为厨师身份查询（默认False）
                - true: 作为厨师身份，查看所有已同意的顾客绑定
                - false: 作为顾客身份，查看自己绑定的所有厨师
        current_user: 当前登录用户（依赖注入）
        db: 数据库会话（依赖注入）

    Returns:
        List[BindingResponse]: 绑定关系列表
    """
    return binding_service.get_my_bindings(db, current_user, as_chef)


@router.delete("/{binding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_binding(
    binding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除绑定关系（顾客或厨师都可以解除绑定）

    Args:
        binding_id: 绑定关系ID
        current_user: 当前登录用户（依赖注入）
        db: 数据库会话（依赖注入）

    Returns:
        None: 204 No Content

    Raises:
        404: 绑定关系不存在
        403: 无权限删除（不是绑定关系的参与者）
    """
    binding_service.delete_binding(db, binding_id, current_user)
    return None
