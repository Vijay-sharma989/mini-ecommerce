from fastapi import APIRouter,Depends,status, HTTPException
from app.models.cart import Cart, CartItem
from app.schemas.cart import CartResponse, CartItemCreate, CartItemResponse, CartDetailsResponse, CartProductResponse, UpdateCardDetails
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.database.dependencies import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.product import Product
from decimal import Decimal


router = APIRouter(
    prefix="/cart",
    tags = ["Cart"]
)

@router.post("/cart", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def create_cart(
    # create_card: CartCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(Cart).where(Cart.user_id==current_user.id))

    existing_cart = result.scalar_one_or_none()

    if existing_cart:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cart Already exist for this user"
        )

    cart = Cart(
        user_id = current_user.id
    )

    db.add(cart)
    await db.commit()
    await db.refresh(cart)
    return cart


@router.post("/card-item", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def cart_item(
    card_item_data : CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    # check whelter the product exists

    product_result = await db.execute(select(Product).where(Product.id==card_item_data.product_id))

    product = product_result.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # 2. Check whether the user already has a cart
    cart_result = await db.execute(select(Cart).where(Cart.user_id==current_user.id))

    cart = cart_result.scalar_one_or_none()

    # 3. Create a cart if one doesn't exist
    if cart is None:

        cart = Cart(
            user_id=current_user.id
        )
        db.add(cart)
        await db.flush()

    # 4. Check whether this product is already in the cart

    item_result = await db.execute(select(CartItem).where(CartItem.cart_id==cart.id, CartItem.product_id==product.id))

    cart_item = item_result.scalar_one_or_none()

    # 5. Calculate the requested total quantity

    new_quantity = card_item_data.quantity

    if cart_item:

        new_quantity = new_quantity + cart_item.quantity

    # check available stock without deducting it
    if new_quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product.stock} units are avaialble"    
        )

    if cart_item:
        cart_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=card_item_data.quantity
        )

        db.add(cart_item)

    await db.commit()
    await db.refresh(cart_item)
    return cart_item


@router.get("/get-cart-items", response_model=CartDetailsResponse)
async def get_cart_details(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    card_result = await db.execute(select(Cart).where(Cart.user_id==current_user.id))

    get_card_data = card_result.scalar_one_or_none()

    if not get_card_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Cart Added"
        )

    cartItem_result = await db.execute(
        select(CartItem, Product).
        join(Product, CartItem.product_id==Product.id)
        .where(CartItem.cart_id==get_card_data.id)
        .order_by(CartItem.id)
        )

    get_all_cardItem = cartItem_result.all()

    items = []

    total_amount = Decimal("0.00")

    for cart_item, product in get_all_cardItem:
        price = Decimal(str(product.price))
        sub_total = price * cart_item.quantity

        items.append(
            CartProductResponse(
                product_id=product.id,
                product_name=product.name,
                price=price,
                quantity=cart_item.quantity,
                sub_total=sub_total
            )
        )

        total_amount = total_amount + sub_total


    return CartDetailsResponse(
        cart_id=get_card_data.id,
        items=items,
        total_amount=total_amount   
    )


@router.put("/update-cart/{cart_item_id}", response_model=CartItemResponse)
async def update_card(
    cart_item_id : int,
    item_data: UpdateCardDetails,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    # find the user cart
    cart_result = await db.execute(select(Cart)
                                   .where(Cart.user_id==current_user.id))

    cart_data = cart_result.scalar_one_or_none()

    if not cart_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="USer has no cart to update"
        )
    
    # find the item inside this user's cart
    item_result = await db.execute(select(CartItem).where(CartItem.id==cart_item_id, CartItem.cart_id==cart_data.id))

    cart_item = item_result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    # Check the product available stock
    product_result = await db.execute(select(Product).where(Product.id==cart_item.product_id))

    product = product_result.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if item_data.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Only {product.stock} unit are available"
        )

    # update quantity
    cart_item.quantity = item_data.quantity

    try:
        await db.commit()
        await db.refresh(cart_item)
    except Exception:
        await db.rollback()
        raise

    return cart_item


@router.delete("/cart-delete/{cartitem_id}/")
async def cart_delete(
    cartitem_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)      
):

    cart_result = await db.execute(select(Cart).where(Cart.user_id==current_user.id))

    cart = cart_result.scalar_one_or_none()

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart is not there for this user"
        )


    cartitem_result = await db.execute(select(CartItem).where(CartItem.id==cartitem_id, CartItem.cart_id==cart.id))

    cart_item = cartitem_result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart Item not available"
        )

    await db.delete(cart_item)
    await db.commit()

    return {
        "message": "Cart item deleted Successfully",
        "cart_item_id": cartitem_id
    }


@router.delete("/clear")
async def clear_cartitem(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Find the current user's cart
    cart_result = await db.execute(
        select(Cart).where(Cart.user_id == current_user.id)
    )
    cart = cart_result.scalar_one_or_none()

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cart available"
        )

    try:
        # 2. Delete all items belonging to this cart
        await db.execute(
            delete(CartItem).where(CartItem.cart_id == cart.id)
        )

        # 3. Save changes
        await db.commit()

    except Exception:
        await db.rollback()
        raise

    return {
        "message": "Cart cleared successfully",
        "cart_id": cart.id
    }
