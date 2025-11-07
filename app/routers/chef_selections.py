from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..schemas.selection import ChefSelectionCreate, ChefSelectionResponse
from ..utils.auth import get_current_user, require_role
from ..services import selection_service

router = APIRouter(prefix="/api/chef-selections", tags=["厨师选菜"])


@router.post("", response_model=ChefSelectionResponse, status_code=status.HTTP_201_CREATED)
def create_chef_selection(
    selection_data: ChefSelectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef"))
):
    """
    厨师选择要制作的菜品

    Args:
        selection_data: 选择数据，包含customer_selection_id和dish_id
        db: 数据库会话（依赖注入）
        current_user: 当前登录用户（依赖注入，需要chef角色）

    Returns:
        ChefSelectionResponse: 创建的选择记录

    Raises:
        404: 客户选择记录不存在
        400: 菜品ID与客户选择不匹配或已选择过该菜品
    """
    return selection_service.create_chef_selection(
        db,
        current_user,
        selection_data.customer_selection_id,
        selection_data.dish_id
    )


@router.get("/my-selections", response_model=List[ChefSelectionResponse])
def get_my_chef_selections(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef"))
):
    """
    获取我的选菜记录（今日）

    Args:
        db: 数据库会话（依赖注入）
        current_user: 当前登录用户（依赖注入，需要chef角色）

    Returns:
        List[ChefSelectionResponse]: 今日的选菜记录列表
    """
    return selection_service.get_my_chef_selections(db, current_user)


@router.delete("/{selection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chef_selection(
    selection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef"))
):
    """
    取消选择

    Args:
        selection_id: 选择记录ID
        db: 数据库会话（依赖注入）
        current_user: 当前登录用户（依赖注入，需要chef角色）

    Returns:
        None: 204 No Content

    Raises:
        404: 选择记录不存在或不属于当前用户
    """
    selection_service.delete_chef_selection(db, current_user, selection_id)
    return None
