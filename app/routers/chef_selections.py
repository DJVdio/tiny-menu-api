from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from ..database import get_db
from ..models.chef_selection import ChefSelection
from ..models.customer_selection import CustomerSelection
from ..models.dish import Dish
from ..models.user import User
from ..schemas.selection import ChefSelectionCreate, ChefSelectionResponse
from ..utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/chef-selections", tags=["厨师选菜"])


@router.post("", response_model=ChefSelectionResponse, status_code=status.HTTP_201_CREATED)
def create_chef_selection(
    selection_data: ChefSelectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef"))
):
    """厨师选择要制作的菜品"""
    # 验证客户选择是否存在
    customer_selection = db.query(CustomerSelection).filter(
        CustomerSelection.id == selection_data.customer_selection_id
    ).first()

    if not customer_selection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer selection not found"
        )

    # 验证菜品ID是否匹配
    if customer_selection.dish_id != selection_data.dish_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dish ID does not match customer selection"
        )

    today = date.today()

    # 检查是否已经选择过
    existing = db.query(ChefSelection).filter(
        ChefSelection.chef_id == current_user.id,
        ChefSelection.customer_selection_id == selection_data.customer_selection_id,
        ChefSelection.date == today
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already selected this dish"
        )

    # 创建厨师选择记录
    new_selection = ChefSelection(
        chef_id=current_user.id,
        customer_selection_id=selection_data.customer_selection_id,
        dish_id=selection_data.dish_id,
        date=today
    )
    db.add(new_selection)
    db.commit()
    db.refresh(new_selection)

    return new_selection


@router.get("/my-selections", response_model=List[ChefSelectionResponse])
def get_my_chef_selections(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef"))
):
    """获取我的选菜记录（今日）"""
    today = date.today()
    selections = db.query(ChefSelection).filter(
        ChefSelection.chef_id == current_user.id,
        ChefSelection.date == today
    ).all()

    return selections


@router.delete("/{selection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chef_selection(
    selection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef"))
):
    """取消选择"""
    selection = db.query(ChefSelection).filter(
        ChefSelection.id == selection_id,
        ChefSelection.chef_id == current_user.id
    ).first()

    if not selection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selection not found"
        )

    db.delete(selection)
    db.commit()

    return None
