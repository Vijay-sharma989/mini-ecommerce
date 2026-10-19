from fastapi import APIRouter, status, Depends, HTTPException, Query
from app.schemas.product import ProductCreate, ProductResponse, UpdateProduct, ProductListResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_db
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.auth.dependencies import required_role, get_current_user
from app.models.enums import UserRole
from sqlalchemy import select
from typing import Optional

router = APIRouter(
    prefix="/products",
    tags=["Product"]
)


@router.post("/product", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(required_role(UserRole.ADMIN, UserRole.SELLER))
    ):

    result = await db.execute(select(Category).where(Category.id==product_data.category_id))

    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {product_data.category_id} not found"
        )

    product = Product(
        name=product_data.name,
        description=product_data.description,
        category_id=product_data.category_id,
        seller_id=current_user.id,
        price=product_data.price,
        stock=product_data.stock,
        image_url=product_data.image_url
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    return product


@router.get('/get-product/', response_model=ProductListResponse)
async def get_all_product(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    cusror: Optional[int] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    query = select(Product)

    #search
    if search:
        query = query.where(Product.name.ilike(f"%{search}"))

    if category_id:
        query = query.where(Product.id==category_id)

    if min_price is not None:
        query = query.where(Product.price>=min_price)

    if max_price is not None:
        query = query.where(Product.price<=max_price)

    if cusror is not None:
        query = query.where(Product.id>cusror)

    #important: always have deterministic ordering
    query = query.order_by(Product.id.asc())

    query = query.limit(limit+1)

    # result = await db.execute(select(Product))
    result = await db.execute(query)

    product = result.scalars().all()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No product Added"
        )

    #Determine whelther there is another page

    has_next = len(product)>limit

    if has_next:
        product = product[:limit]

    next_cursor=None

    if has_next:
        next_cursor = product[-1].id

    # return product
    return {
        "products": product,
        "next_cursor": next_cursor
    }


@router.get('/get-product-id/{product_id}', response_model=ProductResponse)
async def get_product_id(
    product_id:int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(Product).where(Product.id==product_id))

    product = result.scalar_one_or_none()

    if not product:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            details="Product with this id doesn't exist"
        )

    return product


@router.put("/update_product/{product_id}", response_model=ProductResponse)
async def update_product_id(
    product_id: int,
    product_data: UpdateProduct,
    current_user: User = Depends(required_role(UserRole.ADMIN, UserRole.SELLER)),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Product).where(Product.id==product_id))

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if product_data.name is not None:
        product.name=product_data.name

    if product_data.description is not None:
        product.description=product_data.description

    if product_data.price is not None:
        product.price=product_data.price

    if product_data.category_id is not None:
        product.category_id=product_data.category_id

    await db.commit()

    await db.refresh(product)

    return product
