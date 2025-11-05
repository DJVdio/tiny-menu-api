from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta
import random

from ..database import get_db
from ..models.dish import Dish
from ..models.daily_recommendation import DailyRecommendation
from ..models.user import User
from ..schemas.dish import DishCreate, DishResponse, DishWithRecipe
from ..schemas.recommendation import DailyRecommendationResponse
from ..utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/dishes", tags=["菜品管理"])


@router.post("", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
def create_dish(
    dish_data: DishCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef"))
):
    """创建新菜品（仅厨师）"""
    new_dish = Dish(**dish_data.model_dump())
    db.add(new_dish)
    db.commit()
    db.refresh(new_dish)
    return new_dish


@router.get("", response_model=List[DishResponse])
def get_all_dishes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有菜品列表"""
    dishes = db.query(Dish).offset(skip).limit(limit).all()
    return dishes


@router.get("/{dish_id}", response_model=DishWithRecipe)
def get_dish_with_recipe(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取菜品详情（包含菜谱）"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    return dish


@router.get("/recommendations/today", response_model=List[DailyRecommendationResponse])
def get_today_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取今日推荐菜品"""
    today = date.today()

    # 查询今日推荐
    recommendations = db.query(DailyRecommendation).filter(
        DailyRecommendation.date == today
    ).all()

    # 如果今天还没有推荐，则生成推荐
    if not recommendations:
        recommendations = generate_daily_recommendations(db, today)

    return recommendations


def generate_daily_recommendations(db: Session, target_date: date, count: int = 5):
    """生成每日推荐（模拟AI推荐）"""
    # 获取所有菜品
    all_dishes = db.query(Dish).all()

    if not all_dishes:
        return []

    # 随机选择菜品（这里简化处理，实际可以接入AI推荐算法）
    selected_dishes = random.sample(all_dishes, min(count, len(all_dishes)))

    recommendations = []
    for dish in selected_dishes:
        recommendation = DailyRecommendation(
            date=target_date,
            dish_id=dish.id
        )
        db.add(recommendation)
        recommendations.append(recommendation)

    db.commit()

    # 刷新数据以获取关联的dish对象
    for rec in recommendations:
        db.refresh(rec)

    return recommendations


@router.post("/recommendations/generate", response_model=List[DailyRecommendationResponse])
def generate_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef"))
):
    """手动生成今日推荐（仅厨师）"""
    today = date.today()

    # 删除今天已有的推荐
    db.query(DailyRecommendation).filter(
        DailyRecommendation.date == today
    ).delete()
    db.commit()

    # 生成新推荐
    recommendations = generate_daily_recommendations(db, today)

    return recommendations
