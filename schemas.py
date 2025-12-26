from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# Item Schemas
class ItemBase(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Order Item Schemas
class OrderItemCreate(BaseModel):
    item_id: int
    quantity: int


class OrderItemResponse(BaseModel):
    id: int
    item_id: int
    quantity: int
    unit_price: float
    item: ItemResponse

    class Config:
        from_attributes = True


# Order Schemas
class OrderBase(BaseModel):
    customer_name: str
    customer_email: str


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    status: Optional[str] = None
    items: Optional[List[OrderItemCreate]] = None


class OrderResponse(OrderBase):
    id: int
    status: str
    total_amount: float
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True