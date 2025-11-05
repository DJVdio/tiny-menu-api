from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..database import Base


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    recipe = Column(Text, nullable=False)  # 菜谱详细步骤
    ingredients = Column(Text, nullable=False)  # 所需食材
    cooking_time = Column(Integer)  # 烹饪时间（分钟）
    difficulty = Column(String(20))  # 难度：easy, medium, hard
    image_url = Column(String(500))
    category = Column(String(50))  # 菜系分类
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
