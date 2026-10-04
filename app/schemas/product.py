from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    description: str
    category_id: int
    price: Decimal
    stock: int
    image_url: str




class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    category_id: int
    seller_id: int
    price: Decimal
    stock: int
    image_url: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# product = ProductCreate(
#     name="iPhone 17",
#     description="Apple smartphone",
#     category_id=1,
#     price="79999.99",
#     stock=10,
#     image_url="https://example.com/iphone.jpg"
# )

# print(product)
# print(type(product.price))