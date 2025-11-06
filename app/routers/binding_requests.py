"""
绑定请求路由
提供 /api/binding-requests 路径的绑定管理接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.user import User
from ..models.chef_customer_binding import ChefCustomerBinding, BindingStatus
from ..schemas.binding import BindingCreate, BindingUpdate, BindingResponse
from ..utils.auth import get_current_user

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
    """
    # 如果提供了 chefId，验证是否匹配当前用户
    if chefId and str(current_user.id) != chefId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own binding requests"
        )

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


@router.post("", response_model=BindingResponse, status_code=status.HTTP_201_CREATED)
async def create_binding_request(
    binding_data: BindingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建绑定请求
    作为顾客身份申请绑定目标用户（目标用户将作为厨师身份）
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

    # 检查是否已存在绑定关系
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
    """
    # 查找发送给当前用户的绑定请求
    try:
        binding_id = int(request_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID"
        )

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

    # 状态映射：accepted -> approved
    status_mapping = {
        "accepted": "approved",
        "rejected": "rejected",
        "approved": "approved"
    }

    mapped_status = status_mapping.get(binding_update.status.lower())
    if not mapped_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be either 'accepted' or 'rejected'"
        )

    # 更新状态
    binding.status = BindingStatus(mapped_status)
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
