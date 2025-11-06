from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.chef_customer_binding import ChefCustomerBinding, BindingStatus
from ..schemas.binding import BindingCreate, BindingUpdate, BindingResponse
from ..utils.auth import get_current_user

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
    """
    # 查找目标用户（将作为厨师）
    chef = db.query(User).filter(
        User.username == binding_data.chef_username
    ).first()

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
    return BindingResponse(
        id=str(new_binding.id),
        customerId=str(new_binding.customer_id),
        customerName=current_user.nickname,
        chefId=str(new_binding.chef_id),
        chefName=chef.nickname,
        status=new_binding.status.value,
        createdAt=new_binding.created_at.isoformat() if new_binding.created_at else None,
        updatedAt=new_binding.updated_at.isoformat() if new_binding.updated_at else None
    )


@router.get("/pending", response_model=List[BindingResponse])
async def get_pending_bindings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查看待处理的绑定请求
    作为厨师身份查看发送给自己的绑定请求
    """
    # 查询发送给当前用户的待处理绑定请求
    bindings = db.query(ChefCustomerBinding).filter(
        ChefCustomerBinding.chef_id == current_user.id,
        ChefCustomerBinding.status == BindingStatus.PENDING
    ).all()

    result = []
    for binding in bindings:
        customer = db.query(User).filter(User.id == binding.customer_id).first()
        result.append(BindingResponse(
            id=str(binding.id),
            customerId=str(binding.customer_id),
            customerName=customer.nickname,
            chefId=str(binding.chef_id),
            chefName=current_user.nickname,
            status=binding.status.value,
            createdAt=binding.created_at.isoformat() if binding.created_at else None,
            updatedAt=binding.updated_at.isoformat() if binding.updated_at else None
        ))

    return result


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
    """
    # 查找发送给当前用户的绑定请求
    binding = db.query(ChefCustomerBinding).filter(
        ChefCustomerBinding.id == binding_id,
        ChefCustomerBinding.chef_id == current_user.id
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

    # 验证新状态
    if binding_update.status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be either 'approved' or 'rejected'"
        )

    # 更新状态
    binding.status = BindingStatus(binding_update.status)
    db.commit()
    db.refresh(binding)

    customer = db.query(User).filter(User.id == binding.customer_id).first()

    return BindingResponse(
        id=str(binding.id),
        customerId=str(binding.customer_id),
        customerName=customer.nickname,
        chefId=str(binding.chef_id),
        chefName=current_user.nickname,
        status=binding.status.value,
        createdAt=binding.created_at.isoformat() if binding.created_at else None,
        updatedAt=binding.updated_at.isoformat() if binding.updated_at else None
    )


@router.get("/my-bindings", response_model=List[BindingResponse])
async def get_my_bindings(
    as_chef: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
            result.append(BindingResponse(
                id=str(binding.id),
                customerId=str(binding.customer_id),
                customerName=customer.nickname,
                chefId=str(binding.chef_id),
                chefName=current_user.nickname,
                status=binding.status.value,
                createdAt=binding.created_at.isoformat() if binding.created_at else None,
                updatedAt=binding.updated_at.isoformat() if binding.updated_at else None
            ))
    else:
        # 作为顾客：查看自己绑定的所有厨师
        bindings = db.query(ChefCustomerBinding).filter(
            ChefCustomerBinding.customer_id == current_user.id
        ).all()

        result = []
        for binding in bindings:
            chef = db.query(User).filter(User.id == binding.chef_id).first()
            result.append(BindingResponse(
                id=str(binding.id),
                customerId=str(binding.customer_id),
                customerName=current_user.nickname,
                chefId=str(binding.chef_id),
                chefName=chef.nickname,
                status=binding.status.value,
                createdAt=binding.created_at.isoformat() if binding.created_at else None,
                updatedAt=binding.updated_at.isoformat() if binding.updated_at else None
            ))

    return result


@router.delete("/{binding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_binding(
    binding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除绑定关系（顾客或厨师都可以解除绑定）"""
    # 查找绑定关系
    binding = db.query(ChefCustomerBinding).filter(
        ChefCustomerBinding.id == binding_id
    ).first()

    if not binding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Binding not found"
        )

    # 检查权限：只有厨师或顾客本人可以删除
    if binding.chef_id != current_user.id and binding.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this binding"
        )

    db.delete(binding)
    db.commit()

    return None
