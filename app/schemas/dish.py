from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DishBase(BaseModel):
    name: str
    description: Optional[str] = None
    recipe: str
    ingredients: str
    cooking_time: Optional[int] = None
    difficulty: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None


class DishCreate(DishBase):
    pass


class DishResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    cooking_time: Optional[int]
    difficulty: Optional[str]
    image_url: Optional[str]
    category: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DishWithRecipe(DishResponse):
    """包含完整菜谱的菜品信息（用于厨师查看）"""
    recipe: str
    ingredients: str

    class Config:
        from_attributes = True
