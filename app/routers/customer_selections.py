from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from ..database import get_db
from ..models.customer_selection import CustomerSelection
from ..models.dish import Dish
from ..models.user import User
from ..schemas.selection import CustomerSelectionCreate, CustomerSelectionResponse
from ..utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/customer-selections", tags=["客户选菜"])


@router.post("", response_model=CustomerSelectionResponse, status_code=status.HTTP_201_CREATED)
def create_selection(
    selection_data: CustomerSelectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer"))
):
    """客户选择菜品"""
    # 验证菜品是否存在
    dish = db.query(Dish).filter(Dish.id == selection_data.dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )

    today = date.today()

    # 检查是否已经选择过该菜品
    existing_selection = db.query(CustomerSelection).filter(
        CustomerSelection.user_id == current_user.id,
        CustomerSelection.dish_id == selection_data.dish_id,
        CustomerSelection.date == today
    ).first()

    if existing_selection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already selected this dish today"
        )

    # 创建选择记录
    new_selection = CustomerSelection(
        user_id=current_user.id,
        dish_id=selection_data.dish_id,
        date=today
    )
    db.add(new_selection)
    db.commit()
    db.refresh(new_selection)

    return new_selection


@router.get("/my-selections", response_model=List[CustomerSelectionResponse])
def get_my_selections(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer"))
):
    """获取我的选菜记录（今日）"""
    today = date.today()
    selections = db.query(CustomerSelection).filter(
        CustomerSelection.user_id == current_user.id,
        CustomerSelection.date == today
    ).all()

    return selections


@router.delete("/{selection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_selection(
    selection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer"))
):
    """取消选择"""
    selection = db.query(CustomerSelection).filter(
        CustomerSelection.id == selection_id,
        CustomerSelection.user_id == current_user.id
    ).first()

    if not selection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selection not found"
        )

    db.delete(selection)
    db.commit()

    return None


@router.get("/all", response_model=List[CustomerSelectionResponse])
def get_all_customer_selections(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef"))
):
    """获取所有客户的选菜（今日，仅厨师可见）"""
    today = date.today()
    selections = db.query(CustomerSelection).filter(
        CustomerSelection.date == today
    ).all()

    return selections
