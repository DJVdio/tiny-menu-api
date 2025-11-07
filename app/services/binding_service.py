"""
绑定服务层
处理厨师-顾客绑定相关业务逻辑
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from ..models.user import User
from ..models.chef_customer_binding import ChefCustomerBinding, BindingStatus
from ..schemas.binding import BindingResponse


def create_binding_request(db: Session, current_user: User, chef_username: str) -> BindingResponse:
    """
    创建绑定请求
    当前用户作为顾客身份，申请绑定目标用户（目标用户将作为厨师身份）
    """
    # 查找目标用户（将作为厨师）
    chef = db.query(User).filter(User.username == chef_username).first()

    if not chef:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 检查是否试图绑定自己
    if chef.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot bind to yourself"
        )

    # 检查是否已存在绑定关系（包括待审批、已同意的）
    existing_binding = db.query(ChefCustomerBinding).filter(
        ChefCustomerBinding.chef_id == chef.id,
        ChefCustomerBinding.customer_id == current_user.id,
        ChefCustomerBinding.status.in_([BindingStatus.PENDING, BindingStatus.APPROVED])
    ).first()

    if existing_binding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Binding request already exists with status: {existing_binding.status}"
        )

    # 创建新的绑定请求
    new_binding = ChefCustomerBinding(
        chef_id=chef.id,
        customer_id=current_user.id,
        status=BindingStatus.PENDING
    )
    db.add(new_binding)
    db.commit()
    db.refresh(new_binding)

    # 构建响应
    return _build_binding_response(db, new_binding, current_user, chef)


def get_pending_bindings_for_chef(db: Session, chef_user: User) -> List[BindingResponse]:
    """
    查看待处理的绑定请求
    作为厨师身份查看发送给自己的绑定请求
    """
    # 查询发送给当前用户的待处理绑定请求
    bindings = db.query(ChefCustomerBinding).filter(
        ChefCustomerBinding.chef_id == chef_user.id,
        ChefCustomerBinding.status == BindingStatus.PENDING
    ).all()

    result = []
    for binding in bindings:
        customer = db.query(User).filter(User.id == binding.customer_id).first()
        result.append(_build_binding_response(db, binding, customer, chef_user))

    return result


def update_binding_status(
    db: Session,
    binding_id: int,
    chef_user: User,
    new_status: str
) -> BindingResponse:
    """
    同意或拒绝绑定请求
    作为厨师身份处理发送给自己的绑定请求
    """
    # 查找发送给当前用户的绑定请求
    binding = db.query(ChefCustomerBinding).filter(
        ChefCustomerBinding.id == binding_id,
        ChefCustomerBinding.chef_id == chef_user.id
    ).first()

    if not binding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Binding request not found"
        )

    # 检查状态是否为待处理
    if binding.status != BindingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update binding with status: {binding.status}"
        )

    # 状态映射：accepted -> approved
    status_mapping = {
        "accepted": "approved",
        "rejected": "rejected",
        "approved": "approved"
    }

    mapped_status = status_mapping.get(new_status.lower())
    if not mapped_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be either 'accepted', 'approved' or 'rejected'"
        )

    # 更新状态
    binding.status = BindingStatus(mapped_status)
    db.commit()
    db.refresh(binding)

    customer = db.query(User).filter(User.id == binding.customer_id).first()

    return _build_binding_response(db, binding, customer, chef_user)


def get_my_bindings(db: Session, current_user: User, as_chef: bool = False) -> List[BindingResponse]:
    """
    查询我的绑定关系
    - as_chef=true: 作为厨师身份，查看所有已同意的顾客绑定
    - as_chef=false: 作为顾客身份，查看自己绑定的所有厨师
    """
    if as_chef:
        # 作为厨师：查看所有已同意的顾客绑定
        bindings = db.query(ChefCustomerBinding).filter(
            ChefCustomerBinding.chef_id == current_user.id,
            ChefCustomerBinding.status == BindingStatus.APPROVED
        ).all()

        result = []
        for binding in bindings:
            customer = db.query(User).filter(User.id == binding.customer_id).first()
            result.append(_build_binding_response(db, binding, customer, current_user))
    else:
        # 作为顾客：查看自己绑定的所有厨师
        bindings = db.query(ChefCustomerBinding).filter(
            ChefCustomerBinding.customer_id == current_user.id
        ).all()

        result = []
        for binding in bindings:
            chef = db.query(User).filter(User.id == binding.chef_id).first()
            result.append(_build_binding_response(db, binding, current_user, chef))

    return result


def delete_binding(db: Session, binding_id: int, current_user: User) -> None:
    """
    解除绑定关系（顾客或厨师都可以解除绑定，软删除）
    """
    # 查找绑定关系
    binding = db.query(ChefCustomerBinding).filter(
        ChefCustomerBinding.id == binding_id
    ).first()

    if not binding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Binding not found"
        )

    # 检查权限：只有厨师或顾客本人可以解绑
    if binding.chef_id != current_user.id and binding.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to unbind this binding"
        )

    # 检查是否已解绑
    if binding.status == BindingStatus.UNBOUND:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Binding already unbound"
        )

    # 只有已同意的绑定才能解绑
    if binding.status != BindingStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot unbind binding with status: {binding.status}"
        )

    # 软删除：修改状态为 unbound
    binding.status = BindingStatus.UNBOUND
    db.commit()


def _build_binding_response(
    db: Session,
    binding: ChefCustomerBinding,
    customer: User,
    chef: User
) -> BindingResponse:
    """构建绑定响应对象"""
    return BindingResponse(
        id=str(binding.id),
        customerId=str(binding.customer_id),
        customerName=customer.username,
        chefId=str(binding.chef_id),
        chefName=chef.username,
        status=binding.status.value,
        createdAt=binding.created_at.isoformat() if binding.created_at else None,
        updatedAt=binding.updated_at.isoformat() if binding.updated_at else None
    )
