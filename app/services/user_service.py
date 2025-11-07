"""
用户服务层
处理用户注册、登录等业务逻辑
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta

from ..models.user import User
from ..schemas.user import UserCreate, UserResponse, Token
from ..utils.auth import verify_password, get_password_hash, create_access_token
from ..config import settings


def register_user(db: Session, user_data: UserCreate) -> UserResponse:
    """
    用户注册业务逻辑
    """
    # 检查用户名是否存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # 创建新用户
    new_user = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 构建响应
    return UserResponse(
        id=str(new_user.id),
        username=new_user.username,
        name=new_user.username,
        created_at=new_user.created_at
    )


def login_user(db: Session, username: str, password: str) -> Token:
    """
    用户登录业务逻辑
    """
    # 查找用户
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生成JWT令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}, expires_delta=access_token_expires
    )

    # 构建响应
    return Token(
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            name=user.username,
            created_at=user.created_at
        ),
        token=access_token
    )
