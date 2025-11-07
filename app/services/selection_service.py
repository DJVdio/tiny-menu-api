"""
选菜服务层
处理顾客选菜和厨师选择制作相关业务逻辑
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from datetime import date

from ..models.customer_selection import CustomerSelection
from ..models.chef_selection import ChefSelection
from ..models.dish import Dish
from ..models.user import User
from ..models.chef_customer_binding import ChefCustomerBinding, BindingStatus


def create_customer_selection(db: Session, current_user: User, dish_id: int) -> CustomerSelection:
    """客户选择菜品"""
    # 验证菜品是否存在
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )

    today = date.today()

    # 检查是否已经选择过该菜品
    existing_selection = db.query(CustomerSelection).filter(
        CustomerSelection.user_id == current_user.id,
        CustomerSelection.dish_id == dish_id,
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
        dish_id=dish_id,
        date=today
    )
    db.add(new_selection)
    db.commit()
    db.refresh(new_selection)

    return new_selection


def get_my_customer_selections(db: Session, current_user: User) -> List[CustomerSelection]:
    """获取我的选菜记录（今日）"""
    today = date.today()
    selections = db.query(CustomerSelection).filter(
        CustomerSelection.user_id == current_user.id,
        CustomerSelection.date == today
    ).all()

    return selections


def delete_customer_selection(db: Session, current_user: User, selection_id: int) -> None:
    """取消顾客选择"""
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


def get_all_customer_selections_for_chef(db: Session, chef_user: User) -> List[CustomerSelection]:
    """获取已绑定顾客的选菜（今日，仅厨师可见）"""
    today = date.today()

    # 获取所有已绑定的顾客ID
    approved_bindings = db.query(ChefCustomerBinding).filter(
        ChefCustomerBinding.chef_id == chef_user.id,
        ChefCustomerBinding.status == BindingStatus.APPROVED
    ).all()

    bound_customer_ids = [binding.customer_id for binding in approved_bindings]

    # 只返回已绑定顾客的选菜
    selections = db.query(CustomerSelection).filter(
        CustomerSelection.date == today,
        CustomerSelection.user_id.in_(bound_customer_ids)
    ).all()

    return selections


def create_chef_selection(
    db: Session,
    current_user: User,
    customer_selection_id: int,
    dish_id: int
) -> ChefSelection:
    """厨师选择要制作的菜品"""
    # 验证客户选择是否存在
    customer_selection = db.query(CustomerSelection).filter(
        CustomerSelection.id == customer_selection_id
    ).first()

    if not customer_selection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer selection not found"
        )

    # 验证菜品ID是否匹配
    if customer_selection.dish_id != dish_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dish ID does not match customer selection"
        )

    today = date.today()

    # 检查是否已经选择过
    existing = db.query(ChefSelection).filter(
        ChefSelection.chef_id == current_user.id,
        ChefSelection.customer_selection_id == customer_selection_id,
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
        customer_selection_id=customer_selection_id,
        dish_id=dish_id,
        date=today
    )
    db.add(new_selection)
    db.commit()
    db.refresh(new_selection)

    return new_selection


def get_my_chef_selections(db: Session, current_user: User) -> List[ChefSelection]:
    """获取我的选菜记录（今日）"""
    today = date.today()
    selections = db.query(ChefSelection).filter(
        ChefSelection.chef_id == current_user.id,
        ChefSelection.date == today
    ).all()

    return selections


def delete_chef_selection(db: Session, current_user: User, selection_id: int) -> None:
    """取消厨师选择"""
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
