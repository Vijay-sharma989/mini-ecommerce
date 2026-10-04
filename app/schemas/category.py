from pydantic import BaseModel, ConfigDict
from datetime import datetime



class CategoryCreate(BaseModel):
    name: str
    description: str


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)