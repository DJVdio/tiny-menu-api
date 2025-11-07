from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..schemas.selection import CustomerSelectionCreate, CustomerSelectionResponse
from ..utils.auth import get_current_user, require_role
from ..services import selection_service

router = APIRouter(prefix="/api/customer-selections", tags=["客户选菜"])


@router.post("", response_model=CustomerSelectionResponse, status_code=status.HTTP_201_CREATED)
def create_selection(
    selection_data: CustomerSelectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer"))
):
    """
    客户选择菜品

    Args:
        selection_data: 选择数据，包含dish_id
        db: 数据库会话（依赖注入）
        current_user: 当前登录用户（依赖注入，需要customer角色）

    Returns:
        CustomerSelectionResponse: 创建的选择记录

    Raises:
        404: 菜品不存在
        400: 今日已选择过该菜品
    """
    return selection_service.create_customer_selection(db, current_user, selection_data.dish_id)


@router.get("/my-selections", response_model=List[CustomerSelectionResponse])
def get_my_selections(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer"))
):
    """
    获取我的选菜记录（今日）

    Args:
        db: 数据库会话（依赖注入）
        current_user: 当前登录用户（依赖注入，需要customer角色）

    Returns:
        List[CustomerSelectionResponse]: 今日的选菜记录列表
    """
    return selection_service.get_my_customer_selections(db, current_user)


@router.delete("/{selection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_selection(
    selection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer"))
):
    """
    取消选择

    Args:
        selection_id: 选择记录ID
        db: 数据库会话（依赖注入）
        current_user: 当前登录用户（依赖注入，需要customer角色）

    Returns:
        None: 204 No Content

    Raises:
        404: 选择记录不存在或不属于当前用户
    """
    selection_service.delete_customer_selection(db, current_user, selection_id)
    return None


@router.get("/all", response_model=List[CustomerSelectionResponse])
def get_all_customer_selections(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef"))
):
    """
    获取已绑定顾客的选菜（今日，仅厨师可见）

    Args:
        db: 数据库会话（依赖注入）
        current_user: 当前登录用户（依赖注入，需要chef角色）

    Returns:
        List[CustomerSelectionResponse]: 已绑定顾客的今日选菜记录列表
    """
    return selection_service.get_all_customer_selections_for_chef(db, current_user)
