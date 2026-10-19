from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from decimal import Decimal



class CartResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)

class CartProductResponse(BaseModel):
    product_id: int
    product_name: str
    price: Decimal
    quantity: int
    sub_total: Decimal


class CartDetailsResponse(BaseModel):
    cart_id: int
    items: list[CartProductResponse]
    total_amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class UpdateCardDetails(BaseModel):
    quantity: int = Field(ge=1)
    