from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import UserSignup, UserLogin
from app.auth.security import hash_password, verify_password
from app.database.dependencies import get_db
from app.models.user import User
from app.auth.jwt import create_access_token
from app.models.enums import UserRole
from app.auth.dependencies import required_role



router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# @router.get("/admin-test")
# async def admin_test(current_user: User = Depends(required_role(UserRole.ADMIN))):
#     return {
#         "message": "You are admin",
#         "user": current_user.email
#     }


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email==user_data.email))

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email Already Registered"
        )

    user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password)
    )

    db.add(user)

    await db.commit()

    await db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_active": user.is_active,
        "created_at": user.created_at
    }



@router.post('/login', status_code=status.HTTP_200_OK)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email==user_data.email))

    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email and password"
        )

    if not verify_password(user_data.password, existing_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="Invalid email and password"
        )


    access_token = create_access_token(
        {
            "sub": str(existing_user.id)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }