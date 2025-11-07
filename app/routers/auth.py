from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token
from ..services import user_service

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    注册后的用户可以同时作为厨师和顾客使用系统

    Args:
        user_data: 用户注册数据，包含username和password
        db: 数据库会话（依赖注入）

    Returns:
        UserResponse: 注册成功的用户信息

    Raises:
        400: 用户名已存在
    """
    return user_service.register_user(db, user_data)


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录，返回JWT令牌和用户信息

    Args:
        user_data: 登录数据，包含username和password
        db: 数据库会话（依赖注入）

    Returns:
        Token: 包含用户信息和JWT访问令牌

    Raises:
        401: 用户名或密码错误
    """
    return user_service.login_user(db, user_data.username, user_data.password)
