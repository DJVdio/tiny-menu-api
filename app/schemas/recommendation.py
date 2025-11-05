from pydantic import BaseModel
from datetime import date, datetime
from .dish import DishResponse


class DailyRecommendationResponse(BaseModel):
    id: int
    date: date
    dish_id: int
    created_at: datetime
    dish: DishResponse

    class Config:
        from_attributes = True
