from fastapi import Depends, APIRouter

from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
