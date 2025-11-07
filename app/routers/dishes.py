from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..schemas.dish import DishCreate, DishResponse, DishWithRecipe
from ..schemas.recommendation import DailyRecommendationResponse
from ..utils.auth import get_current_user, require_role
from ..services import dish_service

router = APIRouter(prefix="/api/dishes", tags=["菜品管理"])


@router.post("", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
def create_dish(
    dish_data: DishCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef"))
):
    """
    创建新菜品（仅厨师）

    Args:
        dish_data: 菜品数据，包含name, description, recipe, ingredients等信息
        db: 数据库会话（依赖注入）
        current_user: 当前登录用户（依赖注入，需要chef角色）

    Returns:
        DishResponse: 创建的菜品信息
    """
    return dish_service.create_dish(db, dish_data)


@router.get("", response_model=List[DishResponse])
def get_all_dishes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取所有菜品列表

    Args:
        skip: 跳过的记录数（用于分页，默认0）
        limit: 返回的最大记录数（用于分页，默认100）
        db: 数据库会话（依赖注入）
        current_user: 当前登录用户（依赖注入）

    Returns:
        List[DishResponse]: 菜品列表
    """
    return dish_service.get_all_dishes(db, skip, limit)


@router.get("/{dish_id}", response_model=DishWithRecipe)
def get_dish_with_recipe(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取菜品详情（包含菜谱）

    Args:
        dish_id: 菜品ID
        db: 数据库会话（依赖注入）
        current_user: 当前登录用户（依赖注入）

    Returns:
        DishWithRecipe: 菜品详细信息，包含完整菜谱

    Raises:
        404: 菜品不存在
    """
    return dish_service.get_dish_by_id(db, dish_id)


@router.get("/recommendations/today", response_model=List[DailyRecommendationResponse])
def get_today_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取今日推荐菜品

    Args:
        db: 数据库会话（依赖注入）
        current_user: 当前登录用户（依赖注入）

    Returns:
        List[DailyRecommendationResponse]: 今日推荐菜品列表（如果今日没有推荐会自动生成）
    """
    return dish_service.get_today_recommendations(db)


@router.post("/recommendations/generate", response_model=List[DailyRecommendationResponse])
def generate_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef"))
):
    """
    手动重新生成今日推荐（仅厨师）

    Args:
        db: 数据库会话（依赖注入）
        current_user: 当前登录用户（依赖注入，需要chef角色）

    Returns:
        List[DailyRecommendationResponse]: 新生成的今日推荐菜品列表
    """
    return dish_service.regenerate_today_recommendations(db)
