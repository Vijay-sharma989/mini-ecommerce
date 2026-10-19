from fastapi import APIRouter, Depends, HTTPException, status
from app.models.category import Category
from app.auth.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse
from app.database.dependencies import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(
    prefix="/categories",
    tags=['Category']
)

@router.post('/category', response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
    ):
    
    category = Category(
        name=category_data.name,
        description=category_data.description
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)
    return CategoryResponse.model_validate(category)


@router.get('/category', response_model=list[CategoryResponse])
async def get_category(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Category))

    categories = result.scalars().all()

    return categories


@router.get('/category/{category_id}', response_model=CategoryResponse)
async def get_category_id(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    # pass

    result = await db.execute(select(Category).where(Category.id==category_id))

    categories = result.scalar_one_or_none()

    if not categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            details=f"Category {category_id} is not available"
        )

    return categories