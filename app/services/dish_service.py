"""
菜品服务层
处理菜品管理和推荐相关业务逻辑
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from datetime import date
import random

from ..models.dish import Dish
from ..models.daily_recommendation import DailyRecommendation
from ..schemas.dish import DishCreate


def create_dish(db: Session, dish_data: DishCreate) -> Dish:
    """创建新菜品"""
    new_dish = Dish(**dish_data.model_dump())
    db.add(new_dish)
    db.commit()
    db.refresh(new_dish)
    return new_dish


def get_all_dishes(db: Session, skip: int = 0, limit: int = 100) -> List[Dish]:
    """获取所有菜品列表"""
    dishes = db.query(Dish).offset(skip).limit(limit).all()
    return dishes


def get_dish_by_id(db: Session, dish_id: int) -> Dish:
    """获取菜品详情（包含菜谱）"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    return dish


def get_today_recommendations(db: Session) -> List[DailyRecommendation]:
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


def generate_daily_recommendations(db: Session, target_date: date, count: int = 5) -> List[DailyRecommendation]:
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


def regenerate_today_recommendations(db: Session) -> List[DailyRecommendation]:
    """手动重新生成今日推荐"""
    today = date.today()

    # 删除今天已有的推荐
    db.query(DailyRecommendation).filter(
        DailyRecommendation.date == today
    ).delete()
    db.commit()

    # 生成新推荐
    recommendations = generate_daily_recommendations(db, today)

    return recommendations
