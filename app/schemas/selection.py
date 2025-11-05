from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from .dish import DishResponse


class CustomerSelectionCreate(BaseModel):
    dish_id: int


class CustomerSelectionResponse(BaseModel):
    id: int
    user_id: int
    dish_id: int
    date: date
    created_at: datetime
    dish: Optional[DishResponse] = None

    class Config:
        from_attributes = True


class ChefSelectionCreate(BaseModel):
    customer_selection_id: int
    dish_id: int


class ChefSelectionResponse(BaseModel):
    id: int
    chef_id: int
    customer_selection_id: int
    dish_id: int
    date: date
    created_at: datetime
    dish: Optional[DishResponse] = None

    class Config:
        from_attributes = True
